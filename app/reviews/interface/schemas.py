from uuid import UUID

from pydantic import Field

from app.common.schemas import StrictBaseModel
from app.reviews.infrastructure.models import ReviewTargetType


class ReviewCreateRequest(StrictBaseModel):
    target_type: ReviewTargetType
    target_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class ReviewResponse(ReviewCreateRequest):
    id: UUID
    author_id: UUID
