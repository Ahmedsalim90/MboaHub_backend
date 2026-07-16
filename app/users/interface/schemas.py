from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.auth.interface.schemas import UserSummary
from app.common.schemas import StrictBaseModel


class UserUpdateRequest(StrictBaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)


class AddressCreateRequest(StrictBaseModel):
    label: str = Field(min_length=1, max_length=80)
    line1: str = Field(min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    country: str = Field(min_length=2, max_length=80)
    lat: Decimal | None = None
    lng: Decimal | None = None


class AddressResponse(AddressCreateRequest):
    id: UUID
    user_id: UUID


class CurrentUserResponse(UserSummary):
    pass
