from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user
from app.core.database import get_session
from app.reviews.infrastructure.models import Review, ReviewTargetType
from app.reviews.interface.schemas import ReviewCreateRequest, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    payload: ReviewCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    review = Review(author_id=current_user.id, **payload.model_dump())
    session.add(review)
    await session.flush()
    return review


@router.get("", response_model=list[ReviewResponse])
async def list_reviews(
    target_type: ReviewTargetType,
    target_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[ReviewResponse]:
    result = await session.execute(select(Review).where(Review.target_type == target_type, Review.target_id == target_id))
    return list(result.scalars().all())
