from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import Role, User, UserRole, UserStatus


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password_hash: str, full_name: str, phone: str | None) -> User:
        user = User(
            email=email.lower(),
            phone=phone,
            password_hash=password_hash,
            full_name=full_name,
            status=UserStatus.PENDING_VERIFICATION,
            roles=[UserRole(role=Role.CUSTOMER)],
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def add_role(self, user: User, role: Role) -> None:
        if role not in {item.role for item in user.roles}:
            user.roles.append(UserRole(role=role))
            await self.session.flush()
