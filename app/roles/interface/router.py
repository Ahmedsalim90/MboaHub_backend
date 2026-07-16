from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, require_role
from app.core.database import get_session
from app.roles.application.role_request_service import RoleRequestService
from app.roles.interface.schemas import RoleRequestCreate, RoleRequestResponse, RoleRequestReview

router = APIRouter(tags=["role-requests"])


@router.post("/role-requests", response_model=RoleRequestResponse, status_code=201)
async def create_role_request(
    payload: RoleRequestCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RoleRequestResponse:
    return await RoleRequestService(session).create_request(current_user, payload.requested_role, payload.note)


@router.get("/role-requests/me", response_model=list[RoleRequestResponse])
async def list_my_role_requests(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RoleRequestResponse]:
    return await RoleRequestService(session).list_my_requests(current_user)


@router.get("/admin/role-requests", response_model=list[RoleRequestResponse])
async def list_pending_role_requests(
    admin=Depends(require_role("ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> list[RoleRequestResponse]:
    return await RoleRequestService(session).list_pending()


@router.patch("/admin/role-requests/{request_id}/approve", response_model=RoleRequestResponse)
async def approve_role_request(
    request_id: UUID,
    payload: RoleRequestReview,
    admin=Depends(require_role("ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> RoleRequestResponse:
    return await RoleRequestService(session).approve(admin, request_id, payload.reviewer_note)


@router.patch("/admin/role-requests/{request_id}/reject", response_model=RoleRequestResponse)
async def reject_role_request(
    request_id: UUID,
    payload: RoleRequestReview,
    admin=Depends(require_role("ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> RoleRequestResponse:
    return await RoleRequestService(session).reject(admin, request_id, payload.reviewer_note)
