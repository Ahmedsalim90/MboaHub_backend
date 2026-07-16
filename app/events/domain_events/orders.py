from uuid import UUID

from pydantic import BaseModel

from app.orders.infrastructure.models import OrderStatus


class OrderCreated(BaseModel):
    order_id: UUID
    customer_id: UUID
    total_cents: int


class OrderStatusChanged(BaseModel):
    order_id: UUID
    previous_status: OrderStatus
    next_status: OrderStatus
