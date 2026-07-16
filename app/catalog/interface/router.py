from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.application.catalog_service import CatalogService
from app.catalog.interface.schemas import (
    CategoryResponse,
    ProductCreateRequest,
    ProductImageResponse,
    ProductResponse,
    ProductUpdateRequest,
    ShopCreateRequest,
    ShopResponse,
    ShopUpdateRequest,
)
from app.common.dependencies import get_current_user, require_role
from app.common.schemas import ListResponse, PaginationMeta
from app.core.database import get_session

router = APIRouter(tags=["catalog"])


@router.post("/shops", response_model=ShopResponse, status_code=201)
async def create_shop(
    payload: ShopCreateRequest,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> ShopResponse:
    return await CatalogService(session).create_shop(current_user, payload)


@router.get("/shops/{slug}", response_model=ShopResponse)
async def get_shop(slug: str, session: AsyncSession = Depends(get_session)) -> ShopResponse:
    return await CatalogService(session).get_shop_by_slug(slug)


@router.patch("/shops/{shop_id}", response_model=ShopResponse)
async def update_shop(
    shop_id: UUID,
    payload: ShopUpdateRequest,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> ShopResponse:
    return await CatalogService(session).update_shop(current_user, shop_id, payload)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(session: AsyncSession = Depends(get_session)) -> list[CategoryResponse]:
    return await CatalogService(session).list_categories()


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreateRequest,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    return await CatalogService(session).create_product(current_user, payload)


@router.get("/products", response_model=ListResponse[ProductResponse])
async def list_products(
    category_id: UUID | None = None,
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ListResponse[ProductResponse]:
    products = await CatalogService(session).list_products(category_id, search, limit)
    return ListResponse(data=products, meta=PaginationMeta(has_more=False))


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, session: AsyncSession = Depends(get_session)) -> ProductResponse:
    return await CatalogService(session).get_product(product_id)


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    payload: ProductUpdateRequest,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    return await CatalogService(session).update_product(current_user, product_id, payload)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> None:
    await CatalogService(session).delete_product(current_user, product_id)


@router.post("/products/{product_id}/images", response_model=ProductImageResponse, status_code=201)
async def add_product_image(
    product_id: UUID,
    url: str,
    public_id: str,
    position: int = 0,
    current_user=Depends(require_role("SELLER", "ADMIN")),
    session: AsyncSession = Depends(get_session),
) -> ProductImageResponse:
    return await CatalogService(session).add_product_image(current_user, product_id, url, public_id, position)
