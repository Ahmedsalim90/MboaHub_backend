from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReviewTargetType(str, PyEnum):
    PRODUCT = "PRODUCT"
    SHOP = "SHOP"
    RIDER = "RIDER"


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    author_id: Mapped[UUID]
    target_type: Mapped[ReviewTargetType] = mapped_column(SQLEnum(ReviewTargetType), index=True)
    target_id: Mapped[UUID] = mapped_column(index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
