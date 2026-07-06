"""Admin-gated SAML passwordless enrollment integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_saml_automated_rotation import (
    _prepare_rotated_saml_cert_rotation_run,
)


def _prepare_automated_saml_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    rotation_run_id = _prepare_rotated_saml_cert_rotation_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{rotation_run_id}/start",
        headers=admin_headers,
        json={"rotation_summary": "Automated rotation before passwordless enrollment"},
    )
    assert submit.status_code == 200, submit.text
    automated_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/runs/{automated_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "automated"
    return automated_run_id


def test_saml_passwordless_enrollment_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_automated_rotation_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-passwordless-enrollment/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_saml_passwordless_enrollment_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/saml-passwordless-enrollment/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["automated_rotation_ready"] is True
    assert payload["blockers"] == []


def test_submit_saml_passwordless_enrollment_requires_automated_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    rotation_run_id = _prepare_rotated_saml_cert_rotation_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-automated-rotation/rotation-runs/{rotation_run_id}/start",
        headers=admin_headers,
        json={"rotation_summary": "Pending approval — cannot enroll passwordless yet"},
    )
    assert submit.status_code == 200, submit.text
    automated_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{automated_run_id}/enroll",
        headers=admin_headers,
        json={"enrollment_summary": "Attempt passwordless enrollment before automated rotation"},
    )
    assert response.status_code == 409
    assert "not automated" in response.json()["detail"]


def test_submit_and_approve_saml_passwordless_enrollment_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    automated_run_id = _prepare_automated_saml_rotation_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{automated_run_id}/enroll",
        headers=admin_headers,
        json={"enrollment_summary": "Passwordless enrollment after automated SAML rotation"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["saml_automated_rotation_run_id"] == automated_run_id

    approve = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "enrolled"
    assert approved["enrolled_at"] is not None


def test_submit_saml_passwordless_enrollment_unknown_automated_rotation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{uuid.uuid4()}/enroll",
        headers=admin_headers,
        json={"enrollment_summary": "Missing SAML automated rotation run"},
    )
    assert response.status_code == 404


def test_submit_saml_passwordless_enrollment_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    automated_run_id = _prepare_automated_saml_rotation_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{automated_run_id}/enroll",
        headers=readonly_headers,
        json={"enrollment_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_saml_passwordless_enrollment_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    automated_run_id = _prepare_automated_saml_rotation_run(api_client, admin_headers)
    api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{automated_run_id}/enroll",
        headers=admin_headers,
        json={"enrollment_summary": "Listing test passwordless enrollment run"},
    )

    listing = api_client.get(
        "/api/v1/enterprise/federation/saml-passwordless-enrollment/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
