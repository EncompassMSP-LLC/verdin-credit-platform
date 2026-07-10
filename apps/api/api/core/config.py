"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEVELOPMENT_SECRET_KEY = "dev-secret-key-change-in-production-32chars"
_DEVELOPMENT_MINIO_ACCESS_KEY = "minioadmin"
_DEVELOPMENT_MINIO_SECRET_KEY = "minioadmin"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_version: str = "4.2.0"
    app_name: str = "Ultimate Credit Repair LLC API"
    debug: bool = False

    secret_key: str = Field(
        default=_DEVELOPMENT_SECRET_KEY,
        min_length=32,
    )
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    database_url: str = Field(
        default="postgresql+asyncpg://verdin:verdin@localhost:5432/verdin_credit"
    )
    database_url_sync: str = Field(
        default="postgresql://verdin:verdin@localhost:5432/verdin_credit"
    )

    redis_url: str = "redis://localhost:6379/0"
    worker_queue_name: str = "verdin:jobs"
    document_ocr_enabled: bool = True
    document_classification_enabled: bool = True
    document_metadata_enabled: bool = True
    document_entity_resolution_enabled: bool = True

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "verdin-documents"
    minio_secure: bool = False

    document_max_upload_bytes: int = 25 * 1024 * 1024

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    public_app_url: str = "http://localhost:8080"

    dispute_return_name: str = "Ultimate Credit Repair LLC"
    dispute_return_address_line1: str = ""
    dispute_return_address_line2: str = ""
    dispute_return_address_line3: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        if self.app_env != "production":
            return self

        if self.secret_key == _DEVELOPMENT_SECRET_KEY or "change-me" in self.secret_key.lower():
            raise ValueError("Production SECRET_KEY must be explicitly configured")

        if (
            self.minio_access_key == _DEVELOPMENT_MINIO_ACCESS_KEY
            or self.minio_secret_key == _DEVELOPMENT_MINIO_SECRET_KEY
        ):
            raise ValueError("Production MinIO credentials must be explicitly configured")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
