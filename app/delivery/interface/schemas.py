from decimal import Decimal
from uuid import UUID

from app.common.schemas import StrictBaseModel
from app.delivery.infrastructure.models import DeliveryStatus


class DeliveryStatusUpdateRequest(StrictBaseModel):
    status: DeliveryStatus


class DeliveryResponse(StrictBaseModel):
    id: UUID
    order_id: UUID
    rider_id: UUID | None
    status: DeliveryStatus
    pickup_lat: Decimal | None
    pickup_lng: Decimal | None
    dropoff_lat: Decimal | None
    dropoff_lng: Decimal | None
