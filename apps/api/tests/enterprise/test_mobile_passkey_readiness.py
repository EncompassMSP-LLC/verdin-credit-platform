"""Admin-gated mobile passkey readiness integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_bulk_idp_provisioning import _prepare_approved_hris_passwordless_ui_run
from tests.enterprise.test_hris_passwordless_ui import (
    _prepare_enrolled_saml_passwordless_enrollment_run,
)


def test_mobile_passkey_readiness_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/mobile-passkey-readiness/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_mobile_passkey_readiness_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/mobile-passkey-readiness/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["hris_passwordless_ui_ready"] is True
    assert payload["blockers"] == []


def test_submit_mobile_passkey_readiness_requires_approved_ui_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    enrollment_run_id = _prepare_enrolled_saml_passwordless_enrollment_run(
        api_client, admin_headers
    )

    submit_ui = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=admin_headers,
        json={"ui_summary": "Pending approval — cannot start passkey readiness yet"},
    )
    assert submit_ui.status_code == 200, submit_ui.text
    ui_run_id = submit_ui.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"readiness_summary": "Attempt passkey readiness before HRIS UI approved"},
    )
    assert response.status_code == 409
    assert "not approved" in response.json()["detail"]


def test_submit_and_approve_mobile_passkey_readiness_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"readiness_summary": "Web-first passkey readiness after approved HRIS UI"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["hris_passwordless_ui_run_id"] == ui_run_id

    approve = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None


def test_submit_mobile_passkey_readiness_unknown_ui_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"readiness_summary": "Missing HRIS passwordless UI run"},
    )
    assert response.status_code == 404


def test_submit_mobile_passkey_readiness_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{ui_run_id}/start",
        headers=readonly_headers,
        json={"readiness_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_mobile_passkey_readiness_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)
    api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"readiness_summary": "Listing test mobile passkey readiness run"},
    )

    listing = api_client.get(
        "/api/v1/enterprise/federation/mobile-passkey-readiness/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
