from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, require_role
from app.core.database import get_session
from app.delivery.application.delivery_service import DeliveryService
from app.delivery.interface.schemas import DeliveryResponse, DeliveryStatusUpdateRequest

router = APIRouter(prefix="/deliveries", tags=["delivery"])


@router.post("/{order_id}/request-rider", response_model=DeliveryResponse, status_code=201)
async def request_rider(
    order_id: UUID,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> DeliveryResponse:
    return await DeliveryService(session).request_rider(current_user, order_id)


@router.post("/{delivery_id}/accept", response_model=DeliveryResponse)
async def accept_delivery(
    delivery_id: UUID,
    current_user=Depends(require_role("RIDER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> DeliveryResponse:
    return await DeliveryService(session).accept(current_user, delivery_id)


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
async def update_delivery_status(
    delivery_id: UUID,
    payload: DeliveryStatusUpdateRequest,
    current_user=Depends(require_role("RIDER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> DeliveryResponse:
    return await DeliveryService(session).update_status(current_user, delivery_id, payload.status)


@router.post("/{delivery_id}/confirm", response_model=DeliveryResponse)
async def confirm_delivery(
    delivery_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DeliveryResponse:
    return await DeliveryService(session).confirm(current_user, delivery_id)
