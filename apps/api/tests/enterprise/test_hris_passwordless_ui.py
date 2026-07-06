"""Admin-gated HRIS passwordless UI integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_saml_passwordless_enrollment import (
    _prepare_automated_saml_rotation_run,
)


def _prepare_enrolled_saml_passwordless_enrollment_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    automated_run_id = _prepare_automated_saml_rotation_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{automated_run_id}/enroll",
        headers=admin_headers,
        json={"enrollment_summary": "Passwordless enrollment before HRIS UI scaffold"},
    )
    assert submit.status_code == 200, submit.text
    enrollment_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/runs/{enrollment_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "enrolled"
    return enrollment_run_id


def test_hris_passwordless_ui_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    saml_passwordless_enrollment_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-passwordless-ui/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_hris_passwordless_ui_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-passwordless-ui/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["passwordless_enrollment_ready"] is True
    assert payload["blockers"] == []


def test_submit_hris_passwordless_ui_requires_enrolled_enrollment_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    automated_run_id = _prepare_automated_saml_rotation_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{automated_run_id}/enroll",
        headers=admin_headers,
        json={"enrollment_summary": "Pending approval — cannot start HRIS UI yet"},
    )
    assert submit.status_code == 200, submit.text
    enrollment_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=admin_headers,
        json={"ui_summary": "Attempt HRIS UI before passwordless enrollment approved"},
    )
    assert response.status_code == 409
    assert "not enrolled" in response.json()["detail"]


def test_submit_and_approve_hris_passwordless_ui_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    enrollment_run_id = _prepare_enrolled_saml_passwordless_enrollment_run(
        api_client, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=admin_headers,
        json={"ui_summary": "HRIS passwordless UI after enrolled SAML scaffold"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["saml_passwordless_enrollment_run_id"] == enrollment_run_id

    approve = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None


def test_submit_hris_passwordless_ui_unknown_enrollment_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"ui_summary": "Missing SAML passwordless enrollment run"},
    )
    assert response.status_code == 404


def test_submit_hris_passwordless_ui_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    enrollment_run_id = _prepare_enrolled_saml_passwordless_enrollment_run(
        api_client, admin_headers
    )
    response = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=readonly_headers,
        json={"ui_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_hris_passwordless_ui_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    enrollment_run_id = _prepare_enrolled_saml_passwordless_enrollment_run(
        api_client, admin_headers
    )
    api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=admin_headers,
        json={"ui_summary": "Listing test HRIS passwordless UI run"},
    )

    listing = api_client.get(
        "/api/v1/enterprise/federation/hris-passwordless-ui/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
