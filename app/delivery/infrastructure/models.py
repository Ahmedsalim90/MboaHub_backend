from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DeliveryStatus(str, PyEnum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    EN_ROUTE_TO_SELLER = "EN_ROUTE_TO_SELLER"
    PICKED_UP = "PICKED_UP"
    EN_ROUTE_TO_CUSTOMER = "EN_ROUTE_TO_CUSTOMER"
    DELIVERED = "DELIVERED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), unique=True, index=True)
    rider_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[DeliveryStatus] = mapped_column(SQLEnum(DeliveryStatus), default=DeliveryStatus.REQUESTED)
    pickup_lat: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    pickup_lng: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    dropoff_lat: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    dropoff_lng: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RiderLocation(Base):
    __tablename__ = "rider_locations"

    rider_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    lng: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
