"""Worker configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_version: str = "4.2.0"
    redis_url: str = "redis://localhost:6379/0"
    worker_queue_name: str = "verdin:jobs"
    worker_poll_interval_seconds: float = 1.0
    worker_scheduler_interval_seconds: float = 60.0
    worker_job_timeout_seconds: int = 3600
    worker_heartbeat_interval_seconds: int = 30

    database_url_sync: str = "postgresql://verdin:verdin@localhost:5432/verdin_credit"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "verdin-documents"
    minio_secure: bool = False


@lru_cache
def get_worker_settings() -> WorkerSettings:
    return WorkerSettings()
