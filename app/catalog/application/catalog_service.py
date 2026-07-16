from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.infrastructure.models import User
from app.catalog.infrastructure.models import Product, ProductImage, Shop
from app.catalog.infrastructure.repository import CategoryRepository, ProductRepository, ShopRepository
from app.catalog.interface.schemas import ProductCreateRequest, ProductUpdateRequest, ShopCreateRequest, ShopUpdateRequest
from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.shops = ShopRepository(session)
        self.products = ProductRepository(session)
        self.categories = CategoryRepository(session)

    async def create_shop(self, user: User, payload: ShopCreateRequest) -> Shop:
        existing = await self.shops.get_by_owner(user.id)
        if existing is not None:
            raise ConflictException("You already have a shop.")
        shop = Shop(owner_id=user.id, **payload.model_dump())
        return await self.shops.create(shop)

    async def get_shop_by_slug(self, slug: str) -> Shop:
        shop = await self.shops.get_by_slug(slug)
        if shop is None:
            raise NotFoundException("Shop not found.")
        return shop

    async def update_shop(self, user: User, shop_id: UUID, payload: ShopUpdateRequest) -> Shop:
        shop = await self.shops.get_by_id(shop_id)
        if shop is None:
            raise NotFoundException("Shop not found.")
        if shop.owner_id != user.id:
            raise ForbiddenException()
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(shop, field, value)
        return shop

    async def list_categories(self):
        return await self.categories.list_all()

    async def list_products(self, category_id: UUID | None, search: str | None, limit: int) -> list[Product]:
        return await self.products.list_public(category_id=category_id, search=search, limit=limit)

    async def create_product(self, user: User, payload: ProductCreateRequest) -> Product:
        shop = await self.shops.get_by_id(payload.shop_id)
        if shop is None:
            raise NotFoundException("Shop not found.")
        if shop.owner_id != user.id:
            raise ForbiddenException()
        product = Product(**payload.model_dump())
        return await self.products.create(product)

    async def get_product(self, product_id: UUID) -> Product:
        product = await self.products.get_by_id(product_id)
        if product is None:
            raise NotFoundException("Product not found.")
        return product

    async def update_product(self, user: User, product_id: UUID, payload: ProductUpdateRequest) -> Product:
        product = await self.get_product(product_id)
        shop = await self.shops.get_by_id(product.shop_id)
        if shop is None or shop.owner_id != user.id:
            raise ForbiddenException()
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        return product

    async def delete_product(self, user: User, product_id: UUID) -> None:
        product = await self.get_product(product_id)
        shop = await self.shops.get_by_id(product.shop_id)
        if shop is None or shop.owner_id != user.id:
            raise ForbiddenException()
        await self.products.delete(product)

    async def add_product_image(self, user: User, product_id: UUID, url: str, public_id: str, position: int) -> ProductImage:
        product = await self.get_product(product_id)
        shop = await self.shops.get_by_id(product.shop_id)
        if shop is None or shop.owner_id != user.id:
            raise ForbiddenException()
        image = ProductImage(product_id=product_id, url=url, public_id=public_id, position=position)
        self.session.add(image)
        await self.session.flush()
        return image
