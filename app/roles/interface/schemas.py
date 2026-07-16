from uuid import UUID

from pydantic import Field

from app.auth.infrastructure.models import Role
from app.common.schemas import StrictBaseModel
from app.roles.infrastructure.models import RoleRequestStatus


class RoleRequestCreate(StrictBaseModel):
    requested_role: Role
    note: str | None = Field(default=None, max_length=1000)


class RoleRequestReview(StrictBaseModel):
    reviewer_note: str | None = Field(default=None, max_length=1000)


class RoleRequestResponse(StrictBaseModel):
    id: UUID
    user_id: UUID
    requested_role: Role
    status: RoleRequestStatus
    note: str | None
    reviewed_by: UUID | None
    reviewer_note: str | None
