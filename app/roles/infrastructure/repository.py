from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.roles.infrastructure.models import RoleRequest, RoleRequestStatus


class RoleRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, request_id: UUID) -> RoleRequest | None:
        return await self.session.get(RoleRequest, request_id)

    async def get_pending_for_user_and_role(self, user_id: UUID, role) -> RoleRequest | None:
        result = await self.session.execute(
            select(RoleRequest).where(
                RoleRequest.user_id == user_id,
                RoleRequest.requested_role == role,
                RoleRequest.status == RoleRequestStatus.PENDING,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[RoleRequest]:
        result = await self.session.execute(
            select(RoleRequest).where(RoleRequest.user_id == user_id).order_by(RoleRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_status(self, status: RoleRequestStatus, limit: int = 50) -> list[RoleRequest]:
        result = await self.session.execute(
            select(RoleRequest).where(RoleRequest.status == status).order_by(RoleRequest.created_at.asc()).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, role_request: RoleRequest) -> RoleRequest:
        self.session.add(role_request)
        await self.session.flush()
        return role_request
