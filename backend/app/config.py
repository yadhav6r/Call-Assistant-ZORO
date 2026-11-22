from datetime import timedelta
from functools import lru_cache
from typing import Self

from pydantic import EmailStr, Field, SecretStr, model_validator
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
    owner_email: EmailStr | None = None
    live_calls_enabled: bool = False
    exotel_stream_username: SecretStr | None = None
    exotel_stream_password: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    openai_realtime_model: str = "gpt-realtime-2.1"
    openai_realtime_voice: str = "marin"
    live_call_max_seconds: int = Field(default=300, ge=60, le=1800)

    @model_validator(mode="after")
    def require_live_call_credentials(self) -> Self:
        secrets = (
            self.exotel_stream_username,
            self.exotel_stream_password,
            self.openai_api_key,
        )
        if self.live_calls_enabled and not all(
            secret is not None and bool(secret.get_secret_value().strip()) for secret in secrets
        ):
            raise ValueError(
                "Live calls require Exotel stream credentials and an AI API key; "
                "store them as secrets and keep live calls disabled until the provider flow is ready."
            )
        if self.live_calls_enabled and self.app_env.lower() != "production":
            raise ValueError("Live calls can only be enabled in production mode.")
        return self

    @model_validator(mode="after")
    def validate_environment_secrets(self) -> Self:
        if self.app_env.lower() not in {"development", "production"}:
            raise ValueError("ZORO_APP_ENV must be development or production.")
        if self.app_env.lower() == "production":
            jwt_secret = self.jwt_secret_key.get_secret_value()
            database_url = self.database_url.get_secret_value()
            if (
                len(jwt_secret) < 32
                or jwt_secret == "development-only-change-before-use"
                or jwt_secret.lower().startswith("replace")
            ):
                raise ValueError("Production requires a randomly generated JWT secret of at least 32 characters.")
            if (
                not database_url.startswith("postgresql+asyncpg://")
                or "localhost" in database_url
                or "zoro:zoro@" in database_url
                or "replace" in database_url.lower()
            ):
                raise ValueError("Production requires a configured PostgreSQL database URL.")
            if self.owner_email is None:
                raise ValueError("Production requires ZORO_OWNER_EMAIL for the single owner account.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


def refresh_lifetime(settings: Settings) -> timedelta:
    return timedelta(days=settings.refresh_ttl_days)
