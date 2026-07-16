from uuid import UUID

from pydantic import Field

from app.common.schemas import StrictBaseModel
from app.orders.infrastructure.models import OrderStatus


class CartItemCreateRequest(StrictBaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class CartItemUpdateRequest(StrictBaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(StrictBaseModel):
    id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int
    unit_price_cents_snapshot: int


class CheckoutRequest(StrictBaseModel):
    delivery_address_id: UUID


class OrderStatusUpdateRequest(StrictBaseModel):
    status: OrderStatus


class OrderResponse(StrictBaseModel):
    id: UUID
    customer_id: UUID
    shop_id: UUID
    status: OrderStatus
    subtotal_cents: int
    delivery_fee_cents: int
    total_cents: int
    currency: str
    delivery_address_id: UUID
