from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ecosystem API"
    environment: Literal["local", "staging", "production"] = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./ecosystem.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cors_origins: list[AnyHttpUrl] = []
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    stripe_webhook_secret: str = ""
    momo_webhook_secret: str = ""
    # Email that gets auto-promoted to ADMIN on startup. This is how you
    # bootstrap your first admin: register a normal account with this email
    # via /auth/register, then restart the app (or redeploy) - it will be
    # promoted automatically. Leave empty to disable.
    admin_bootstrap_email: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
