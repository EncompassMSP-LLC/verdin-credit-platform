"""HRIS bidirectional sync integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.enterprise_identity import get_enterprise_identity_settings
from api.core.feature_flags import get_feature_flags
from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunKind

VALID_SAML_METADATA = """<?xml version="1.0"?>
<EntityDescriptor entityID="https://idp.example.com/metadata"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"/>
</EntityDescriptor>"""


@pytest.fixture
def hris_sync_env(
    monkeypatch: pytest.MonkeyPatch,
    federation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_FEDERATION_METADATA", "true")
    monkeypatch.setenv("ENABLE_HRIS_BIDIRECTIONAL_SYNC", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def saml_metadata_only_env(
    monkeypatch: pytest.MonkeyPatch,
    federation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_FEDERATION_METADATA", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


def test_hris_sync_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_metadata_only_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-sync/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_hris_sync_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-sync/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["saml_metadata_ready"] is True
    assert payload["blockers"] == []


def test_run_hris_sync_without_saml_metadata(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/federation/hris-sync/run",
        headers=admin_headers,
        json={"run_kind": HrisBidirectionalSyncRunKind.EMPLOYEES_INBOUND.value},
    )
    assert response.status_code == 404
    assert "SAML federation metadata" in response.json()["detail"]


def test_run_hris_sync_after_metadata_upload(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    upload = api_client.post(
        "/api/v1/enterprise/federation/saml-metadata/upload",
        headers=admin_headers,
        json={
            "metadata_xml": VALID_SAML_METADATA,
            "provider_key": "workday-hris",
        },
    )
    assert upload.status_code == 200, upload.text

    response = api_client.post(
        "/api/v1/enterprise/federation/hris-sync/run",
        headers=admin_headers,
        json={"run_kind": HrisBidirectionalSyncRunKind.EMPLOYEES_INBOUND.value},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["run"]["status"] == "completed"
    assert body["run"]["records_synced"] == 1
    assert body["run"]["records_skipped"] == 0


def test_run_hris_sync_requires_write_role(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/enterprise/federation/hris-sync/run",
        headers=readonly_headers,
        json={"run_kind": HrisBidirectionalSyncRunKind.EMPLOYEES_INBOUND.value},
    )
    assert response.status_code == 403


def test_list_hris_sync_runs_empty(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-sync/runs",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["items"] == []
    assert payload["total"] == 0
