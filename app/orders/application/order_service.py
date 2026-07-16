from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.catalog.infrastructure.repository import ProductRepository, ShopRepository
from app.common.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.events.event_bus import EventBus
from app.events.domain_events.orders import OrderCreated, OrderStatusChanged
from app.orders.domain.state_machine import assert_order_transition
from app.orders.infrastructure.models import CartItem, Order, OrderItem, OrderStatus
from app.orders.infrastructure.repository import CartRepository, OrderRepository


class OrderService:
    def __init__(self, session: AsyncSession, event_bus: EventBus | None = None) -> None:
        self.session = session
        self.carts = CartRepository(session)
        self.orders = OrderRepository(session)
        self.products = ProductRepository(session)
        self.shops = ShopRepository(session)
        self.event_bus = event_bus or EventBus()

    async def get_cart(self, user: User) -> list[CartItem]:
        cart = await self.carts.get_or_create_for_user(user.id)
        return await self.carts.list_items(cart.id)

    async def add_cart_item(self, user: User, product_id: UUID, quantity: int) -> CartItem:
        product = await self.products.get_by_id(product_id)
        if product is None:
            raise NotFoundException("Product not found.")
        cart = await self.carts.get_or_create_for_user(user.id)
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            unit_price_cents_snapshot=product.price_cents,
        )
        return await self.carts.add_item(item)

    async def update_cart_item(self, user: User, item_id: UUID, quantity: int) -> CartItem:
        item = await self.carts.get_item(item_id)
        if item is None:
            raise NotFoundException("Cart item not found.")
        cart = await self.carts.get_or_create_for_user(user.id)
        if item.cart_id != cart.id:
            raise ForbiddenException()
        item.quantity = quantity
        return item

    async def delete_cart_item(self, user: User, item_id: UUID) -> None:
        item = await self.carts.get_item(item_id)
        if item is None:
            raise NotFoundException("Cart item not found.")
        cart = await self.carts.get_or_create_for_user(user.id)
        if item.cart_id != cart.id:
            raise ForbiddenException()
        await self.session.delete(item)

    async def checkout(self, user: User, delivery_address_id: UUID, idempotency_key: str | None) -> Order:
        if not idempotency_key:
            raise BadRequestException("Idempotency-Key header is required for checkout.")
        cart = await self.carts.get_or_create_for_user(user.id)
        cart_items = await self.carts.list_items(cart.id)
        if not cart_items:
            raise BadRequestException("Your cart is empty.")
        product = await self.products.get_by_id(cart_items[0].product_id)
        if product is None:
            raise NotFoundException("A product in your cart no longer exists.")
        subtotal = sum(item.quantity * item.unit_price_cents_snapshot for item in cart_items)
        delivery_fee = 500
        order = Order(
            customer_id=user.id,
            shop_id=product.shop_id,
            status=OrderStatus.PENDING_PAYMENT,
            subtotal_cents=subtotal,
            delivery_fee_cents=delivery_fee,
            total_cents=subtotal + delivery_fee,
            currency=product.currency,
            delivery_address_id=delivery_address_id,
        )
        order_items = [
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price_cents_snapshot=item.unit_price_cents_snapshot,
            )
            for item in cart_items
        ]
        created_order = await self.orders.create(order, order_items)
        await self.event_bus.publish(OrderCreated(order_id=created_order.id, customer_id=user.id, total_cents=created_order.total_cents))
        return created_order

    async def get_order(self, user: User, order_id: UUID) -> Order:
        order = await self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundException("Order not found.")
        if order.customer_id != user.id:
            shop = await self.shops.get_by_owner(user.id)
            if shop is None or shop.id != order.shop_id:
                raise ForbiddenException()
        return order

    async def list_orders(self, user: User) -> list[Order]:
        return await self.orders.list_for_user(user.id)

    async def update_status(self, user: User, order_id: UUID, next_status: OrderStatus) -> Order:
        order = await self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundException("Order not found.")
        shop = await self.shops.get_by_owner(user.id)
        if shop is None or shop.id != order.shop_id:
            raise ForbiddenException()
        previous = order.status
        assert_order_transition(previous, next_status)
        order.status = next_status
        await self.event_bus.publish(OrderStatusChanged(order_id=order.id, previous_status=previous, next_status=next_status))
        return order
