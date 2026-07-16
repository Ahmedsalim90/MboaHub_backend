from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.catalog.infrastructure.repository import ShopRepository
from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.delivery.domain.state_machine import assert_delivery_transition
from app.delivery.infrastructure.models import Delivery, DeliveryStatus
from app.delivery.infrastructure.repository import DeliveryRepository
from app.events.domain_events.delivery import RiderAssigned, RiderRequested
from app.events.event_bus import EventBus
from app.orders.infrastructure.repository import OrderRepository


class DeliveryService:
    def __init__(self, session: AsyncSession, event_bus: EventBus | None = None) -> None:
        self.session = session
        self.deliveries = DeliveryRepository(session)
        self.orders = OrderRepository(session)
        self.shops = ShopRepository(session)
        self.event_bus = event_bus or EventBus()

    async def request_rider(self, user: User, order_id: UUID) -> Delivery:
        order = await self.orders.get_by_id(order_id)
        if order is None:
            raise NotFoundException("Order not found.")
        shop = await self.shops.get_by_owner(user.id)
        if shop is None or shop.id != order.shop_id:
            raise ForbiddenException()
        existing = await self.deliveries.get_by_order_id(order_id)
        if existing is not None:
            raise ConflictException("A rider has already been requested for this order.")
        delivery = await self.deliveries.create(
            Delivery(order_id=order_id, status=DeliveryStatus.REQUESTED, requested_at=datetime.now(timezone.utc))
        )
        await self.event_bus.publish(RiderRequested(delivery_id=delivery.id, order_id=order_id))
        return delivery

    async def accept(self, rider: User, delivery_id: UUID) -> Delivery:
        delivery = await self._get(delivery_id)
        assert_delivery_transition(delivery.status, DeliveryStatus.ACCEPTED)
        delivery.status = DeliveryStatus.ACCEPTED
        delivery.rider_id = rider.id
        delivery.accepted_at = datetime.now(timezone.utc)
        await self.event_bus.publish(RiderAssigned(delivery_id=delivery.id, rider_id=rider.id))
        return delivery

    async def update_status(self, rider: User, delivery_id: UUID, status: DeliveryStatus) -> Delivery:
        delivery = await self._get(delivery_id)
        if delivery.rider_id != rider.id:
            raise ForbiddenException()
        assert_delivery_transition(delivery.status, status)
        delivery.status = status
        now = datetime.now(timezone.utc)
        if status == DeliveryStatus.PICKED_UP:
            delivery.picked_up_at = now
        if status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = now
        return delivery

    async def confirm(self, customer: User, delivery_id: UUID) -> Delivery:
        delivery = await self._get(delivery_id)
        order = await self.orders.get_by_id(delivery.order_id)
        if order is None or order.customer_id != customer.id:
            raise ForbiddenException()
        assert_delivery_transition(delivery.status, DeliveryStatus.CONFIRMED)
        delivery.status = DeliveryStatus.CONFIRMED
        delivery.confirmed_at = datetime.now(timezone.utc)
        return delivery

    async def _get(self, delivery_id: UUID) -> Delivery:
        delivery = await self.deliveries.get_by_id(delivery_id)
        if delivery is None:
            raise NotFoundException("Delivery not found.")
        return delivery
