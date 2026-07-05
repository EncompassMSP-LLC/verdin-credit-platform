"""Admin-gated SAML automated rotation integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_saml_certificate_rotation import (
    _upload_valid_saml_metadata,
)


def _prepare_rotated_saml_cert_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    metadata_upload_id = _upload_valid_saml_metadata(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/metadata-uploads/{metadata_upload_id}/rotate",
        headers=admin_headers,
        json={"rotation_summary": "Manual rotation before automated scaffold"},
    )
    assert submit.status_code == 200, submit.text
    rotation_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/runs/{rotation_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "rotated"
    return rotation_run_id


def test_saml_automated_rotation_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_cert_rotation_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-automated-rotation/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_saml_automated_rotation_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-automated-rotation/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["cert_rotation_ready"] is True
    assert payload["blockers"] == []


def test_submit_saml_automated_rotation_requires_rotated_cert_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    metadata_upload_id = _upload_valid_saml_metadata(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-cert-rotation/metadata-uploads/{metadata_upload_id}/rotate",
        headers=admin_headers,
        json={"rotation_summary": "Pending approval — cannot start automated rotation yet"},
    )
    assert submit.status_code == 200, submit.text
    rotation_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{rotation_run_id}/start",
        headers=admin_headers,
        json={"rotation_summary": "Attempt automated rotation before cert run rotated"},
    )
    assert response.status_code == 409
    assert "not rotated" in response.json()["detail"]


def test_submit_and_approve_saml_automated_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    rotation_run_id = _prepare_rotated_saml_cert_rotation_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{rotation_run_id}/start",
        headers=admin_headers,
        json={"rotation_summary": "Automated SAML cert rotation after manual rotation"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["saml_certificate_rotation_run_id"] == rotation_run_id

    approve = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "automated"
    assert approved["automated_at"] is not None


def test_submit_saml_automated_rotation_unknown_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"rotation_summary": "Missing SAML certificate rotation run"},
    )
    assert response.status_code == 404


def test_submit_saml_automated_rotation_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    rotation_run_id = _prepare_rotated_saml_cert_rotation_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{rotation_run_id}/start",
        headers=readonly_headers,
        json={"rotation_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_saml_automated_rotation_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    rotation_run_id = _prepare_rotated_saml_cert_rotation_run(api_client, admin_headers)
    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{rotation_run_id}/start",
        headers=admin_headers,
        json={"rotation_summary": "Listing test automated rotation run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get(
        "/api/v1/enterprise/federation/saml-automated-rotation/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
