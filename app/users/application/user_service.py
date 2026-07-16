from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.auth.interface.schemas import UserSummary
from app.users.infrastructure.models import Address
from app.users.infrastructure.repository import AddressRepository
from app.users.interface.schemas import AddressCreateRequest


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def summarize(self, user: User) -> UserSummary:
        return UserSummary(
            id=user.id,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            status=user.status,
            roles=[role.role for role in user.roles],
        )

    async def update_me(self, user: User, full_name: str | None, phone: str | None) -> UserSummary:
        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone = phone
        return self.summarize(user)

    async def list_addresses(self, user: User) -> list[Address]:
        return await AddressRepository(self.session).list_for_user(user.id)

    async def create_address(self, user: User, payload: AddressCreateRequest) -> Address:
        address = Address(user_id=user.id, **payload.model_dump())
        return await AddressRepository(self.session).create(address)
