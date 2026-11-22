from datetime import timedelta
from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ZORO_", extra="ignore")

    app_env: str = "development"
    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://zoro:zoro@localhost:5432/zoro"
    )
    database_pool_size: int = Field(default=5, ge=1, le=30)
    database_max_overflow: int = Field(default=5, ge=0, le=30)
    jwt_secret_key: SecretStr = SecretStr("development-only-change-before-use")
    jwt_access_ttl_minutes: int = Field(default=15, ge=5, le=60)
    refresh_ttl_days: int = Field(default=30, ge=1, le=90)

    @model_validator(mode="after")
    def require_development_only_auth_until_verification_exists(self) -> "Settings":
        if self.app_env.lower() != "development":
            raise ValueError(
                "Authentication is development-only until email verification and production "
                "secret configuration are implemented."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


def refresh_lifetime(settings: Settings) -> timedelta:
    return timedelta(days=settings.refresh_ttl_days)
