"""Multi-IdP federation integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.enterprise_identity import get_enterprise_identity_settings
from api.core.feature_flags import get_feature_flags


@pytest.fixture
def federation_env(monkeypatch: pytest.MonkeyPatch, enterprise_oidc_env: None) -> None:
    monkeypatch.setenv("ENABLE_IDP_FEDERATION", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


def test_federation_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_oidc_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/federation/status", headers=admin_headers)
    assert response.status_code == 404


def test_federation_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    federation_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/federation/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["provider_count"] == 0
    assert payload["blockers"] == []


def test_register_federation_provider_and_list(
    api_client: TestClient,
    admin_headers: dict[str, str],
    federation_env: None,
) -> None:
    create = api_client.post(
        "/api/v1/enterprise/federation/providers",
        headers=admin_headers,
        json={
            "provider_key": "okta-primary",
            "provider_type": "oidc",
            "display_name": "Okta Primary",
            "issuer_url": "https://okta.example.com",
            "is_primary": True,
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["provider_key"] == "okta-primary"
    assert body["is_primary"] is True

    listing = api_client.get("/api/v1/enterprise/federation/providers", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total_results"] == 1

    status_response = api_client.get(
        "/api/v1/enterprise/federation/status",
        headers=admin_headers,
    )
    assert status_response.json()["provider_count"] == 1


def test_register_federation_provider_duplicate_conflict(
    api_client: TestClient,
    admin_headers: dict[str, str],
    federation_env: None,
) -> None:
    payload = {
        "provider_key": "azure-backup",
        "provider_type": "saml",
        "display_name": "Azure Backup",
    }
    first = api_client.post(
        "/api/v1/enterprise/federation/providers",
        headers=admin_headers,
        json=payload,
    )
    assert first.status_code == 201, first.text

    second = api_client.post(
        "/api/v1/enterprise/federation/providers",
        headers=admin_headers,
        json=payload,
    )
    assert second.status_code == 409


def test_register_federation_provider_requires_oidc_issuer(
    api_client: TestClient,
    admin_headers: dict[str, str],
    federation_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/federation/providers",
        headers=admin_headers,
        json={
            "provider_key": "missing-issuer",
            "provider_type": "oidc",
            "display_name": "Missing Issuer",
        },
    )
    assert response.status_code == 422


def test_register_federation_provider_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    federation_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/federation/providers",
        headers=readonly_headers,
        json={
            "provider_key": "readonly",
            "provider_type": "saml",
            "display_name": "Read Only",
        },
    )
    assert response.status_code == 403
