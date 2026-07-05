"""Admin-gated SAML certificate rotation integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.conftest import VALID_SAML_METADATA


def _upload_valid_saml_metadata(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    upload = api_client.post(
        "/api/v1/enterprise/federation/saml-metadata/upload",
        headers=admin_headers,
        json={
            "metadata_xml": VALID_SAML_METADATA,
            "provider_key": "okta-federation",
        },
    )
    assert upload.status_code == 200, upload.text
    return upload.json()["upload"]["id"]


def test_saml_cert_rotation_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-cert-rotation/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_saml_cert_rotation_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_cert_rotation_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-cert-rotation/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["hris_sync_ready"] is True
    assert payload["blockers"] == []


def test_submit_and_approve_saml_certificate_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_cert_rotation_env: None,
) -> None:
    metadata_upload_id = _upload_valid_saml_metadata(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/metadata-uploads/{metadata_upload_id}/rotate",
        headers=admin_headers,
        json={"rotation_summary": "Rotate IdP signing certificate after operator review"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    assert submit.json()["run"]["status"] == "pending_approval"
    assert submit.json()["run"]["metadata_upload_id"] == metadata_upload_id

    approve = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "rotated"
    assert approve.json()["run"]["rotated_at"] is not None


def test_submit_saml_cert_rotation_invalid_metadata_upload(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_cert_rotation_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/metadata-uploads/{uuid.uuid4()}/rotate",
        headers=admin_headers,
        json={"rotation_summary": "Should fail without metadata upload"},
    )
    assert response.status_code == 404


def test_submit_saml_cert_rotation_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    saml_cert_rotation_env: None,
) -> None:
    metadata_upload_id = _upload_valid_saml_metadata(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/metadata-uploads/{metadata_upload_id}/rotate",
        headers=readonly_headers,
        json={"rotation_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_saml_certificate_rotation_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_cert_rotation_env: None,
) -> None:
    metadata_upload_id = _upload_valid_saml_metadata(api_client, admin_headers)
    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/metadata-uploads/{metadata_upload_id}/rotate",
        headers=admin_headers,
        json={"rotation_summary": "Listing test rotation run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get(
        "/api/v1/enterprise/federation/saml-cert-rotation/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["metadata_upload_id"] == metadata_upload_id
