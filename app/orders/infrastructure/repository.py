from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.orders.infrastructure.models import Cart, CartItem, Order, OrderItem


class CartRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create_for_user(self, user_id: UUID) -> Cart:
        result = await self.session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        if cart is None:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            await self.session.flush()
        return cart

    async def list_items(self, cart_id: UUID) -> list[CartItem]:
        result = await self.session.execute(select(CartItem).where(CartItem.cart_id == cart_id))
        return list(result.scalars().all())

    async def get_item(self, item_id: UUID) -> CartItem | None:
        return await self.session.get(CartItem, item_id)

    async def add_item(self, item: CartItem) -> CartItem:
        self.session.add(item)
        await self.session.flush()
        return item


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        return await self.session.get(Order, order_id)

    async def list_for_user(self, user_id: UUID) -> list[Order]:
        result = await self.session.execute(select(Order).where(Order.customer_id == user_id).order_by(Order.created_at.desc()))
        return list(result.scalars().all())

    async def create(self, order: Order, items: list[OrderItem]) -> Order:
        self.session.add(order)
        await self.session.flush()
        for item in items:
            item.order_id = order.id
            self.session.add(item)
        await self.session.flush()
        return order
