from uuid import UUID

from app.auth.infrastructure.models import UserStatus
from app.common.schemas import StrictBaseModel


class AdminUserStatusUpdate(StrictBaseModel):
    status: UserStatus


class AnalyticsSummary(StrictBaseModel):
    total_users: int
    total_orders: int
    total_disputes: int


class DisputeSummary(StrictBaseModel):
    id: UUID
    status: str
