"""Organization admin and API key lifecycle tests."""

from fastapi.testclient import TestClient

from api.core.api_keys import API_KEY_PREFIX, hash_api_key, verify_api_key
from api.core.org_admin import get_org_admin_status
from api.modules.org_admin.models import ApiKeyScope


def test_api_key_material_helpers() -> None:
    full_key = f"{API_KEY_PREFIX}test-secret-value"
    key_hash = hash_api_key(full_key)
    assert verify_api_key(full_key, key_hash) is True
    assert verify_api_key("wrong-key", key_hash) is False


def test_org_admin_status_payload() -> None:
    status = get_org_admin_status()
    assert status.org_admin_enabled is True
    assert status.api_keys_enabled is True
    assert "api_key_lifecycle" in status.capabilities


def test_org_admin_endpoints_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_disabled: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/status", headers=admin_headers)
    assert response.status_code == 404


def test_get_org_admin_status(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["org_admin_enabled"] is True
    assert payload["api_keys_enabled"] is True
    assert "organization_summary" in payload["capabilities"]


def test_get_organization_summary(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/organization", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["name"] == "Org Admin Test Organization"
    assert payload["active_user_count"] >= 1
    assert payload["active_api_key_count"] == 0


def test_org_admin_requires_admin_role(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get("/api/v1/org-admin/status", headers=manager_headers)
    assert response.status_code == 403


def test_api_key_create_list_get_revoke_flow(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    create_response = api_client.post(
        "/api/v1/org-admin/api-keys",
        headers=admin_headers,
        json={
            "name": "Integration Key",
            "scopes": [ApiKeyScope.READ.value, ApiKeyScope.WRITE.value],
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["name"] == "Integration Key"
    assert created["key_prefix"].startswith(API_KEY_PREFIX[:8])
    assert created["api_key"].startswith(API_KEY_PREFIX)
    assert created["is_active"] is True
    api_key_id = created["id"]

    list_response = api_client.get("/api/v1/org-admin/api-keys", headers=admin_headers)
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 1
    assert listed[0]["id"] == api_key_id
    assert "api_key" not in listed[0]

    get_response = api_client.get(
        f"/api/v1/org-admin/api-keys/{api_key_id}",
        headers=admin_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Integration Key"

    revoke_response = api_client.post(
        f"/api/v1/org-admin/api-keys/{api_key_id}/revoke",
        headers=admin_headers,
    )
    assert revoke_response.status_code == 200
    revoked = revoke_response.json()
    assert revoked["is_active"] is False
    assert revoked["revoked_at"] is not None

    duplicate_revoke = api_client.post(
        f"/api/v1/org-admin/api-keys/{api_key_id}/revoke",
        headers=admin_headers,
    )
    assert duplicate_revoke.status_code == 400


def test_create_api_key_requires_scopes(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.post(
        "/api/v1/org-admin/api-keys",
        headers=admin_headers,
        json={"name": "No Scopes Key", "scopes": []},
    )
    assert response.status_code == 422
