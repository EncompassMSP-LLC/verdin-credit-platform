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

    # LRP-109 — production organization mode guardrails
    allow_demo_orgs: bool = Field(
        default=True,
        description="ALLOW_DEMO_ORGS — when false, demo capabilities are disabled globally",
    )
    enable_sample_data: bool = Field(
        default=True,
        description="ENABLE_SAMPLE_DATA — allow sample/demo data APIs for non-production orgs",
    )
    enable_demo_login: bool = Field(
        default=True,
        description="ENABLE_DEMO_LOGIN — server-side hint; production UI still forces demo auth off",
    )

    # LRP-103 — public referral web-form intake
    referral_intake_enabled: bool = Field(
        default=True,
        description="REFERRAL_INTAKE_ENABLED — accept public partner referral form posts",
    )
    referral_intake_organization_slug: str = Field(
        default="verdin-demo",
        description="REFERRAL_INTAKE_ORGANIZATION_SLUG — CRO org that owns web-form referrals",
    )

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

        # LRP-109: never allow demo pathways when APP_ENV=production
        # (env vars documented for clarity; production always forces them off).
        self.allow_demo_orgs = False
        self.enable_sample_data = False
        self.enable_demo_login = False

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
