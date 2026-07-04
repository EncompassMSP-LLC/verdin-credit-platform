"""API developer portal and key rotation tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.api_keys import API_KEY_PREFIX
from api.core.feature_flags import get_feature_flags
from api.core.org_admin import get_org_admin_status
from api.modules.org_admin.models import ApiKeyScope


@pytest.fixture
def developer_portal_env(monkeypatch: pytest.MonkeyPatch, enterprise_enabled: None) -> None:
    monkeypatch.setenv("ENABLE_API_DEVELOPER_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def test_developer_portal_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/developer-portal", headers=admin_headers)
    assert response.status_code == 404


def test_get_developer_portal(
    api_client: TestClient,
    admin_headers: dict[str, str],
    developer_portal_env: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/developer-portal", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["rotation_enabled"] is True
    assert payload["blockers"] == []
    assert "rate_limit" in payload
    assert isinstance(payload["api_keys"], list)


def test_rotate_api_key_flow(
    api_client: TestClient,
    admin_headers: dict[str, str],
    developer_portal_env: None,
) -> None:
    create_response = api_client.post(
        "/api/v1/org-admin/api-keys",
        headers=admin_headers,
        json={"name": "Rotate Me", "scopes": [ApiKeyScope.READ.value]},
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    old_full_key = created["api_key"]
    api_key_id = created["id"]

    rotate_response = api_client.post(
        f"/api/v1/org-admin/api-keys/{api_key_id}/rotate",
        headers=admin_headers,
    )
    assert rotate_response.status_code == 200, rotate_response.text
    rotated = rotate_response.json()
    assert rotated["api_key"].startswith(API_KEY_PREFIX)
    assert rotated["api_key"] != old_full_key
    assert rotated["previous_key"]["id"] == api_key_id
    assert rotated["previous_key"]["is_active"] is False
    assert rotated["previous_key"]["revoked_at"] is not None
    assert rotated["new_key"]["is_active"] is True
    assert rotated["new_key"]["name"] == "Rotate Me"

    list_response = api_client.get("/api/v1/org-admin/api-keys", headers=admin_headers)
    assert list_response.status_code == 200
    keys = list_response.json()
    assert len(keys) == 2
    active_keys = [key for key in keys if key["is_active"] and key["revoked_at"] is None]
    assert len(active_keys) == 1
    assert active_keys[0]["id"] == rotated["new_key"]["id"]


def test_rotate_revoked_key_rejected(
    api_client: TestClient,
    admin_headers: dict[str, str],
    developer_portal_env: None,
) -> None:
    create_response = api_client.post(
        "/api/v1/org-admin/api-keys",
        headers=admin_headers,
        json={"name": "Revoked Key", "scopes": [ApiKeyScope.READ.value]},
    )
    api_key_id = create_response.json()["id"]
    revoke_response = api_client.post(
        f"/api/v1/org-admin/api-keys/{api_key_id}/revoke",
        headers=admin_headers,
    )
    assert revoke_response.status_code == 200

    rotate_response = api_client.post(
        f"/api/v1/org-admin/api-keys/{api_key_id}/rotate",
        headers=admin_headers,
    )
    assert rotate_response.status_code == 400


def test_org_admin_includes_developer_portal_capabilities(
    developer_portal_env: None,
) -> None:
    status = get_org_admin_status()
    assert "api_key_rotation" in status.capabilities
    assert "developer_portal" in status.capabilities
    assert "api_key_rotation" not in status.deferred_capabilities
