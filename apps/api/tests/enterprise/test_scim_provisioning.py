"""SCIM provisioning integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.enterprise_identity import get_enterprise_identity_settings
from api.core.feature_flags import get_feature_flags


@pytest.fixture
def scim_env(monkeypatch: pytest.MonkeyPatch, enterprise_oidc_env: None) -> None:
    monkeypatch.setenv("ENABLE_SCIM_PROVISIONING", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


def test_scim_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    scim_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/scim/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["blockers"] == []


def test_provision_scim_user_and_list(
    api_client: TestClient,
    admin_headers: dict[str, str],
    scim_env: None,
) -> None:
    create = api_client.post(
        "/api/v1/enterprise/scim/v2/Users",
        headers=admin_headers,
        json={
            "userName": "jordan.scim@verdin.example",
            "externalId": "ext-user-001",
            "active": True,
            "name": {"givenName": "Jordan", "familyName": "Sample"},
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["userName"] == "Jordan Sample"
    assert body["externalId"] == "ext-user-001"
    assert body["active"] is True

    listing = api_client.get("/api/v1/enterprise/scim/v2/Users", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["totalResults"] == 1


def test_provision_scim_group(
    api_client: TestClient,
    admin_headers: dict[str, str],
    scim_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/scim/v2/Groups",
        headers=admin_headers,
        json={"displayName": "Case Managers", "externalId": "ext-group-001"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["displayName"] == "Case Managers"

    listing = api_client.get("/api/v1/enterprise/scim/v2/Groups", headers=admin_headers)
    assert listing.status_code == 200
    assert listing.json()["totalResults"] == 1


def test_scim_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_oidc_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/scim/status", headers=admin_headers)
    assert response.status_code == 404


def test_scim_provision_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    scim_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/scim/v2/Users",
        headers=readonly_headers,
        json={"userName": "reader@verdin.example", "externalId": "ext-readonly"},
    )
    assert response.status_code == 403
