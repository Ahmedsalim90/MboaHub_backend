from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.auth.infrastructure.repository import UserRepository
from app.common.exceptions import BadRequestException, ConflictException, NotFoundException
from app.roles.infrastructure.models import REQUESTABLE_ROLES, RoleRequest, RoleRequestStatus
from app.roles.infrastructure.repository import RoleRequestRepository


class RoleRequestService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.requests = RoleRequestRepository(session)
        self.users = UserRepository(session)

    async def create_request(self, user: User, requested_role, note: str | None) -> RoleRequest:
        if requested_role not in REQUESTABLE_ROLES:
            raise BadRequestException(
                f"{requested_role.value} cannot be self-requested.",
                {"requestable_roles": [role.value for role in REQUESTABLE_ROLES]},
            )
        if requested_role in {role.role for role in user.roles}:
            raise ConflictException("You already have this role.")
        existing = await self.requests.get_pending_for_user_and_role(user.id, requested_role)
        if existing is not None:
            raise ConflictException("You already have a pending request for this role.")
        role_request = RoleRequest(user_id=user.id, requested_role=requested_role, note=note)
        return await self.requests.create(role_request)

    async def list_my_requests(self, user: User) -> list[RoleRequest]:
        return await self.requests.list_for_user(user.id)

    async def list_pending(self) -> list[RoleRequest]:
        return await self.requests.list_by_status(RoleRequestStatus.PENDING)

    async def approve(self, admin: User, request_id: UUID, reviewer_note: str | None) -> RoleRequest:
        role_request = await self._get_pending(request_id)
        target_user = await self.users.get_by_id(role_request.user_id)
        if target_user is None:
            raise NotFoundException("The requesting user no longer exists.")
        await self.users.add_role(target_user, role_request.requested_role)
        role_request.status = RoleRequestStatus.APPROVED
        role_request.reviewed_by = admin.id
        role_request.reviewer_note = reviewer_note
        return role_request

    async def reject(self, admin: User, request_id: UUID, reviewer_note: str | None) -> RoleRequest:
        role_request = await self._get_pending(request_id)
        role_request.status = RoleRequestStatus.REJECTED
        role_request.reviewed_by = admin.id
        role_request.reviewer_note = reviewer_note
        return role_request

    async def _get_pending(self, request_id: UUID) -> RoleRequest:
        role_request = await self.requests.get_by_id(request_id)
        if role_request is None:
            raise NotFoundException("Role request not found.")
        if role_request.status != RoleRequestStatus.PENDING:
            raise ConflictException(f"This request has already been {role_request.status.value.lower()}.")
        return role_request
