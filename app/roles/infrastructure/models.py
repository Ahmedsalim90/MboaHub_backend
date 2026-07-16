from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.infrastructure.models import Role
from app.core.database import Base, TimestampMixin


class RoleRequestStatus(str, PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Roles a user is allowed to self-request. ADMIN and CUSTOMER are deliberately
# excluded: CUSTOMER is granted automatically at registration, and ADMIN is
# never self-service (see app/roles/README_ADMIN_BOOTSTRAP.md).
REQUESTABLE_ROLES = {Role.SELLER, Role.RIDER, Role.EMPLOYER, Role.JOB_SEEKER}


class RoleRequest(TimestampMixin, Base):
    __tablename__ = "role_requests"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    requested_role: Mapped[Role] = mapped_column(SQLEnum(Role))
    status: Mapped[RoleRequestStatus] = mapped_column(SQLEnum(RoleRequestStatus), default=RoleRequestStatus.PENDING, index=True)
    note: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    reviewer_note: Mapped[str | None] = mapped_column(Text)
