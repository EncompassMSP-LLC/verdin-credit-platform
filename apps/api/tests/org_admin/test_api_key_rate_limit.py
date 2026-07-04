"""API key rate limiting tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.api_key_rate_limit import (
    ApiKeyRateLimitExceededError,
    InMemoryApiKeyRateLimiter,
    get_api_key_rate_limit_settings,
    set_api_key_rate_limiter,
)
from api.core.feature_flags import get_feature_flags


@pytest.fixture
def rate_limit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_API_KEY_RATE_LIMIT", "true")
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("API_KEY_RATE_LIMIT_PER_MINUTE", "2")
    get_feature_flags.cache_clear()
    get_api_key_rate_limit_settings.cache_clear()
    limiter = InMemoryApiKeyRateLimiter(limit_per_minute=2)
    set_api_key_rate_limiter(limiter)
    yield
    set_api_key_rate_limiter(None)
    get_feature_flags.cache_clear()
    get_api_key_rate_limit_settings.cache_clear()


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_blocks_after_limit() -> None:
    import uuid

    limiter = InMemoryApiKeyRateLimiter(limit_per_minute=2)
    org_id = uuid.uuid4()
    key_id = uuid.uuid4()
    await limiter.enforce(organization_id=org_id, api_key_id=key_id)
    await limiter.enforce(organization_id=org_id, api_key_id=key_id)
    with pytest.raises(ApiKeyRateLimitExceededError):
        await limiter.enforce(organization_id=org_id, api_key_id=key_id)


def test_api_key_rate_limit_returns_429_on_reporting_operations(
    api_client: TestClient,
    read_api_key: tuple[str, object],
    enterprise_enabled: None,
    rate_limit_env: None,
) -> None:
    full_key, _ = read_api_key
    headers = {"X-API-Key": full_key}
    for _ in range(2):
        response = api_client.get("/api/v1/reporting/operations", headers=headers)
        assert response.status_code == 200, response.text

    blocked = api_client.get("/api/v1/reporting/operations", headers=headers)
    assert blocked.status_code == 429
    assert blocked.headers.get("retry-after") == "60"


def test_api_key_rate_limit_status_endpoint(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
    rate_limit_env: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/api-keys/rate-limit/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["limit_per_minute"] == 2
    assert payload["backend"] == "redis"


def test_org_admin_status_includes_rate_limit_capability(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
    rate_limit_env: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "api_key_rate_limiting" in payload["capabilities"]
    assert "api_key_rate_limiting" not in payload["deferred_capabilities"]
