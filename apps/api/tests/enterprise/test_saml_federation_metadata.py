"""SAML federation metadata upload integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.enterprise_identity import get_enterprise_identity_settings
from api.core.feature_flags import get_feature_flags

VALID_SAML_METADATA = """<?xml version="1.0"?>
<EntityDescriptor entityID="https://idp.example.com/metadata"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"/>
</EntityDescriptor>"""


@pytest.fixture
def saml_metadata_env(
    monkeypatch: pytest.MonkeyPatch,
    federation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_FEDERATION_METADATA", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


def test_saml_metadata_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    federation_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-metadata/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_saml_metadata_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_metadata_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-metadata/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["federation_ready"] is True
    assert payload["blockers"] == []


def test_upload_valid_saml_metadata_and_list(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_metadata_env: None,
) -> None:
    upload = api_client.post(
        "/api/v1/enterprise/federation/saml-metadata/upload",
        headers=admin_headers,
        json={
            "metadata_xml": VALID_SAML_METADATA,
            "provider_key": "okta-saml",
        },
    )
    assert upload.status_code == 200, upload.text
    body = upload.json()
    assert body["upload"]["entity_id"] == "https://idp.example.com/metadata"
    assert body["upload"]["provider_key"] == "okta-saml"
    assert body["upload"]["validation_status"] == "valid"

    listing = api_client.get(
        "/api/v1/enterprise/federation/saml-metadata/uploads",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] == 1


def test_upload_invalid_saml_metadata_rejected(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_metadata_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/federation/saml-metadata/upload",
        headers=admin_headers,
        json={"metadata_xml": "<root/>"},
    )
    assert response.status_code == 422


def test_upload_saml_metadata_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    saml_metadata_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/federation/saml-metadata/upload",
        headers=readonly_headers,
        json={"metadata_xml": VALID_SAML_METADATA},
    )
    assert response.status_code == 403
