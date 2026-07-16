from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, require_role
from app.core.database import get_session
from app.orders.application.order_service import OrderService
from app.orders.interface.schemas import (
    CartItemCreateRequest,
    CartItemResponse,
    CartItemUpdateRequest,
    CheckoutRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
)

router = APIRouter(tags=["orders"])


@router.get("/cart", response_model=list[CartItemResponse])
async def get_cart(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[CartItemResponse]:
    return await OrderService(session).get_cart(current_user)


@router.post("/cart/items", response_model=CartItemResponse, status_code=201)
async def add_cart_item(
    payload: CartItemCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CartItemResponse:
    return await OrderService(session).add_cart_item(current_user, payload.product_id, payload.quantity)


@router.patch("/cart/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: UUID,
    payload: CartItemUpdateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CartItemResponse:
    return await OrderService(session).update_cart_item(current_user, item_id, payload.quantity)


@router.delete("/cart/items/{item_id}", status_code=204)
async def delete_cart_item(
    item_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await OrderService(session).delete_cart_item(current_user, item_id)


@router.post("/orders/checkout", response_model=OrderResponse, status_code=201)
async def checkout(
    payload: CheckoutRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    return await OrderService(session).checkout(current_user, payload.delivery_address_id, idempotency_key)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    return await OrderService(session).get_order(current_user, order_id)


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[OrderResponse]:
    return await OrderService(session).list_orders(current_user)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdateRequest,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    return await OrderService(session).update_status(current_user, order_id, payload.status)
