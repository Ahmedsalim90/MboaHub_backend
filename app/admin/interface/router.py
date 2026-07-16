from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.interface.schemas import AdminUserStatusUpdate, AnalyticsSummary, DisputeSummary
from app.auth.infrastructure.models import User
from app.auth.interface.schemas import UserSummary
from app.common.dependencies import require_role
from app.core.database import get_session
from app.orders.infrastructure.models import Order, OrderStatus
from app.orders.interface.schemas import OrderResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserSummary])
async def list_users(admin=Depends(require_role("ADMIN")), session: AsyncSession = Depends(get_session)) -> list[UserSummary]:
    result = await session.execute(select(User).limit(100))
    users = result.scalars().all()
    return [
        UserSummary(
            id=user.id,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            status=user.status,
            roles=[role.role for role in user.roles],
        )
        for user in users
    ]


@router.patch("/users/{user_id}/status", response_model=UserSummary)
async def update_user_status(
    user_id: UUID,
    payload: AdminUserStatusUpdate,
    admin=Depends(require_role("ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> UserSummary:
    user = await session.get(User, user_id)
    user.status = payload.status
    return UserSummary(
        id=user.id,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        status=user.status,
        roles=[role.role for role in user.roles],
    )


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(admin=Depends(require_role("ADMIN")), session: AsyncSession = Depends(get_session)) -> list[OrderResponse]:
    result = await session.execute(select(Order).limit(100))
    return list(result.scalars().all())


@router.get("/disputes", response_model=list[DisputeSummary])
async def list_disputes(admin=Depends(require_role("ADMIN")), session: AsyncSession = Depends(get_session)) -> list[DisputeSummary]:
    result = await session.execute(select(Order).where(Order.status == OrderStatus.DISPUTED).limit(100))
    return [DisputeSummary(id=order.id, status=order.status.value) for order in result.scalars().all()]


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def analytics_summary(admin=Depends(require_role("ADMIN")), session: AsyncSession = Depends(get_session)) -> AnalyticsSummary:
    user_count = await session.scalar(select(func.count()).select_from(User))
    order_count = await session.scalar(select(func.count()).select_from(Order))
    dispute_count = await session.scalar(select(func.count()).select_from(Order).where(Order.status == OrderStatus.DISPUTED))
    return AnalyticsSummary(total_users=user_count or 0, total_orders=order_count or 0, total_disputes=dispute_count or 0)
