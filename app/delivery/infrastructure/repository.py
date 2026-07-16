from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.infrastructure.models import Delivery


class DeliveryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        return await self.session.get(Delivery, delivery_id)

    async def get_by_order_id(self, order_id: UUID) -> Delivery | None:
        result = await self.session.execute(select(Delivery).where(Delivery.order_id == order_id))
        return result.scalar_one_or_none()

    async def create(self, delivery: Delivery) -> Delivery:
        self.session.add(delivery)
        await self.session.flush()
        return delivery
