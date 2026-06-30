"""Security review tests for runtime configuration."""

import pytest
from pydantic import ValidationError

from api.core.config import Settings


def test_production_rejects_default_secret_key() -> None:
    with pytest.raises(ValidationError, match="Production SECRET_KEY"):
        Settings(
            app_env="production",
            secret_key="dev-secret-key-change-in-production-32chars",
            minio_access_key="prod-access-key",
            minio_secret_key="prod-secret-key",
        )


def test_production_rejects_default_minio_credentials() -> None:
    with pytest.raises(ValidationError, match="Production MinIO credentials"):
        Settings(
            app_env="production",
            secret_key="production-secret-key-at-least-32-characters",
        )


def test_production_accepts_explicit_secret_values() -> None:
    settings = Settings(
        app_env="production",
        secret_key="production-secret-key-at-least-32-characters",
        minio_access_key="prod-access-key",
        minio_secret_key="prod-secret-key",
    )
    assert settings.app_env == "production"
