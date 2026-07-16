from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class PaginationMeta(StrictBaseModel):
    next_cursor: str | None = None
    has_more: bool = False


class ListResponse(StrictBaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta
