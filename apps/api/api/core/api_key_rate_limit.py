"""Per-organization API key rate limiting scaffold."""

from __future__ import annotations

import asyncio
import time
import uuid
from functools import lru_cache
from typing import Protocol

import redis
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.config import get_settings
from api.core.feature_flags import FeatureFlag, is_feature_enabled


class ApiKeyRateLimitExceededError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__("API key rate limit exceeded")


class ApiKeyRateLimitSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key_rate_limit_per_minute: int = Field(default=60, ge=1)


class ApiKeyRateLimitStatus:
    def __init__(
        self,
        *,
        enabled: bool,
        limit_per_minute: int,
        backend: str,
    ) -> None:
        self.enabled = enabled
        self.limit_per_minute = limit_per_minute
        self.backend = backend


class ApiKeyRateLimiter(Protocol):
    async def enforce(
        self,
        *,
        organization_id: uuid.UUID,
        api_key_id: uuid.UUID,
    ) -> None: ...


def _current_window() -> int:
    return int(time.time()) // 60


def _window_key(organization_id: uuid.UUID, api_key_id: uuid.UUID, window: int) -> str:
    return f"api_key_rl:{organization_id}:{api_key_id}:{window}"


class NoopApiKeyRateLimiter:
    async def enforce(
        self,
        *,
        organization_id: uuid.UUID,
        api_key_id: uuid.UUID,
    ) -> None:
        _ = (organization_id, api_key_id)


class InMemoryApiKeyRateLimiter:
    """In-memory fixed-window limiter for tests and local development."""

    def __init__(self, *, limit_per_minute: int) -> None:
        self._limit_per_minute = limit_per_minute
        self._counts: dict[str, int] = {}

    async def enforce(
        self,
        *,
        organization_id: uuid.UUID,
        api_key_id: uuid.UUID,
    ) -> None:
        key = _window_key(organization_id, api_key_id, _current_window())
        count = self._counts.get(key, 0) + 1
        self._counts[key] = count
        if count > self._limit_per_minute:
            raise ApiKeyRateLimitExceededError(retry_after_seconds=60)


class RedisApiKeyRateLimiter:
    """Redis-backed fixed-window limiter for API key authenticated routes."""

    def __init__(self, *, redis_url: str, limit_per_minute: int) -> None:
        self._redis_url = redis_url
        self._limit_per_minute = limit_per_minute
        self._client: redis.Redis | None = None

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    def _enforce_sync(
        self,
        *,
        organization_id: uuid.UUID,
        api_key_id: uuid.UUID,
    ) -> None:
        client = self._get_client()
        key = _window_key(organization_id, api_key_id, _current_window())
        count = int(client.incr(key))
        if count == 1:
            client.expire(key, 60)
        if count > self._limit_per_minute:
            ttl = int(client.ttl(key))
            retry_after = ttl if ttl > 0 else 60
            raise ApiKeyRateLimitExceededError(retry_after_seconds=retry_after)

    async def enforce(
        self,
        *,
        organization_id: uuid.UUID,
        api_key_id: uuid.UUID,
    ) -> None:
        await asyncio.to_thread(
            self._enforce_sync,
            organization_id=organization_id,
            api_key_id=api_key_id,
        )


_rate_limiter_override: ApiKeyRateLimiter | None = None


def set_api_key_rate_limiter(limiter: ApiKeyRateLimiter | None) -> None:
    global _rate_limiter_override
    _rate_limiter_override = limiter


@lru_cache
def get_api_key_rate_limit_settings() -> ApiKeyRateLimitSettings:
    return ApiKeyRateLimitSettings()


def get_api_key_rate_limit_status() -> ApiKeyRateLimitStatus:
    settings = get_api_key_rate_limit_settings()
    enabled = is_feature_enabled(FeatureFlag.ENABLE_API_KEY_RATE_LIMIT)
    backend = "redis" if enabled else "disabled"
    return ApiKeyRateLimitStatus(
        enabled=enabled,
        limit_per_minute=settings.api_key_rate_limit_per_minute,
        backend=backend,
    )


def get_api_key_rate_limiter() -> ApiKeyRateLimiter:
    if _rate_limiter_override is not None:
        return _rate_limiter_override
    if not is_feature_enabled(FeatureFlag.ENABLE_API_KEY_RATE_LIMIT):
        return NoopApiKeyRateLimiter()
    settings = get_api_key_rate_limit_settings()
    return RedisApiKeyRateLimiter(
        redis_url=get_settings().redis_url,
        limit_per_minute=settings.api_key_rate_limit_per_minute,
    )


async def enforce_api_key_rate_limit(
    *,
    organization_id: uuid.UUID,
    api_key_id: uuid.UUID,
    limiter: ApiKeyRateLimiter | None = None,
) -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_API_KEY_RATE_LIMIT):
        return
    provider = limiter or get_api_key_rate_limiter()
    await provider.enforce(organization_id=organization_id, api_key_id=api_key_id)
