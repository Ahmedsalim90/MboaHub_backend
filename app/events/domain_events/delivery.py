from uuid import UUID

from pydantic import BaseModel


class RiderRequested(BaseModel):
    delivery_id: UUID
    order_id: UUID


class RiderAssigned(BaseModel):
    delivery_id: UUID
    rider_id: UUID
