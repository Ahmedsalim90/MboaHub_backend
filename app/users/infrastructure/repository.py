from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.infrastructure.models import Address


class AddressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, user_id: UUID) -> list[Address]:
        result = await self.session.execute(select(Address).where(Address.user_id == user_id))
        return list(result.scalars().all())

    async def create(self, address: Address) -> Address:
        self.session.add(address)
        await self.session.flush()
        return address
