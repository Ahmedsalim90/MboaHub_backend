from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.infrastructure.models import Category, Product, ProductStatus, Shop


class ShopRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, shop_id: UUID) -> Shop | None:
        return await self.session.get(Shop, shop_id)

    async def get_by_slug(self, slug: str) -> Shop | None:
        result = await self.session.execute(select(Shop).where(Shop.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> Shop | None:
        result = await self.session.execute(select(Shop).where(Shop.owner_id == owner_id))
        return result.scalar_one_or_none()

    async def create(self, shop: Shop) -> Shop:
        self.session.add(shop)
        await self.session.flush()
        return shop


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        return await self.session.get(Product, product_id)

    async def list_public(
        self,
        status: ProductStatus = ProductStatus.ACTIVE,
        category_id: UUID | None = None,
        search: str | None = None,
        limit: int = 20,
    ) -> list[Product]:
        query = select(Product).where(Product.status == status).limit(limit)
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        if search:
            query = query.where(Product.title.ilike(f"%{search}%"))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)
