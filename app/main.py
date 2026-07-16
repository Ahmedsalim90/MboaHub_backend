from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.interface.router import router as admin_router
from app.auth.interface.router import router as auth_router
from app.catalog.interface.router import router as catalog_router
from app.chat.interface.router import router as chat_router
from app.chat.websocket import router as websocket_router
from app.common.exception_handlers import register_exception_handlers
from app.common.middleware import register_middleware
from app.core.config import get_settings
from app.core import model_registry
from app.core.database import get_session_factory
from app.delivery.interface.router import router as delivery_router
from app.orders.interface.router import router as orders_router
from app.payments.interface.router import router as payments_router
from app.reviews.interface.router import router as reviews_router
from app.roles.interface.router import router as roles_router
from app.users.interface.router import router as users_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins] or ["http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_middleware(app)
    register_exception_handlers(app)

    prefix = settings.api_v1_prefix
    app.include_router(auth_router, prefix=prefix)
    app.include_router(users_router, prefix=prefix)
    app.include_router(catalog_router, prefix=prefix)
    app.include_router(orders_router, prefix=prefix)
    app.include_router(delivery_router, prefix=prefix)
    app.include_router(payments_router, prefix=prefix)
    app.include_router(chat_router, prefix=prefix)
    app.include_router(reviews_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(roles_router, prefix=prefix)
    app.include_router(websocket_router)

    @app.on_event("startup")
    async def bootstrap_admin() -> None:
        email = settings.admin_bootstrap_email.strip().lower()
        if not email:
            return
        from app.auth.infrastructure.models import Role
        from app.auth.infrastructure.repository import UserRepository

        async with get_session_factory()() as session:
            async with session.begin():
                repo = UserRepository(session)
                user = await repo.get_by_email(email)
                if user is None:
                    return
                if Role.ADMIN not in {role.role for role in user.roles}:
                    await repo.add_role(user, Role.ADMIN)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
