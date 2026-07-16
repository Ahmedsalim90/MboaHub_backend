from uuid import UUID

from pydantic import Field

from app.catalog.infrastructure.models import ProductStatus, VerificationStatus
from app.common.schemas import StrictBaseModel


class ShopCreateRequest(StrictBaseModel):
    name: str = Field(min_length=2, max_length=140)
    slug: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = Field(default=None, max_length=2000)


class ShopUpdateRequest(StrictBaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    description: str | None = Field(default=None, max_length=2000)


class ShopResponse(StrictBaseModel):
    id: UUID
    owner_id: UUID
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    verification_status: VerificationStatus


class CategoryResponse(StrictBaseModel):
    id: UUID
    name: str
    slug: str
    parent_id: UUID | None


class ProductCreateRequest(StrictBaseModel):
    shop_id: UUID
    category_id: UUID | None = None
    title: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=220, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = Field(default=None, max_length=5000)
    price_cents: int = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    stock_quantity: int = Field(ge=0)
    sku: str | None = Field(default=None, max_length=80)
    status: ProductStatus = ProductStatus.DRAFT


class ProductUpdateRequest(StrictBaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    price_cents: int | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    status: ProductStatus | None = None


class ProductResponse(StrictBaseModel):
    id: UUID
    shop_id: UUID
    category_id: UUID | None
    title: str
    slug: str
    description: str | None
    price_cents: int
    currency: str
    stock_quantity: int
    sku: str | None
    status: ProductStatus


class ProductImageResponse(StrictBaseModel):
    id: UUID
    product_id: UUID
    url: str
    public_id: str
    position: int
