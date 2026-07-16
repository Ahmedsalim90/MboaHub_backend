from uuid import UUID

from pydantic import Field

from app.auth.infrastructure.models import Role, UserStatus
from app.common.schemas import StrictBaseModel


class RegisterRequest(StrictBaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)


class LoginRequest(StrictBaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(StrictBaseModel):
    refresh_token: str


class VerifyOtpRequest(StrictBaseModel):
    phone: str = Field(min_length=5, max_length=32)
    otp: str = Field(min_length=4, max_length=8)


class UserSummary(StrictBaseModel):
    id: UUID
    email: str
    phone: str | None
    full_name: str
    status: UserStatus
    roles: list[Role]


class TokenResponse(StrictBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserSummary


class MessageResponse(StrictBaseModel):
    message: str
