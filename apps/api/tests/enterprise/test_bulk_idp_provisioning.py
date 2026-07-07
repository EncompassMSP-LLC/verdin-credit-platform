"""Admin-gated multi-IdP bulk provisioning integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_hris_passwordless_ui import (
    _prepare_enrolled_saml_passwordless_enrollment_run,
)


def _prepare_approved_hris_passwordless_ui_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    enrollment_run_id = _prepare_enrolled_saml_passwordless_enrollment_run(
        api_client, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=admin_headers,
        json={"ui_summary": "HRIS UI before bulk IdP provisioning scaffold"},
    )
    assert submit.status_code == 200, submit.text
    ui_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/runs/{ui_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "approved"
    return ui_run_id


def test_bulk_idp_provisioning_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_passwordless_ui_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/bulk-idp-provisioning/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_bulk_idp_provisioning_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    bulk_idp_provisioning_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/bulk-idp-provisioning/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["hris_passwordless_ui_ready"] is True
    assert payload["blockers"] == []


def test_submit_bulk_idp_provisioning_requires_approved_ui_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    bulk_idp_provisioning_env: None,
) -> None:
    enrollment_run_id = _prepare_enrolled_saml_passwordless_enrollment_run(
        api_client, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/enterprise/federation/hris-passwordless-ui/enrollment-runs/{enrollment_run_id}/start",
        headers=admin_headers,
        json={"ui_summary": "Pending approval — cannot start bulk provisioning yet"},
    )
    assert submit.status_code == 200, submit.text
    ui_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/bulk-idp-provisioning/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"provisioning_summary": "Attempt bulk provisioning before UI approved"},
    )
    assert response.status_code == 409
    assert "not approved" in response.json()["detail"]


def test_submit_and_approve_bulk_idp_provisioning_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    bulk_idp_provisioning_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/bulk-idp-provisioning/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"provisioning_summary": "Bulk IdP provisioning after approved HRIS UI"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["hris_passwordless_ui_run_id"] == ui_run_id

    approve = api_client.post(
        f"/api/v1/enterprise/federation/bulk-idp-provisioning/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "provisioned"
    assert approved["provisioned_at"] is not None


def test_submit_bulk_idp_provisioning_unknown_ui_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    bulk_idp_provisioning_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/bulk-idp-provisioning/ui-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"provisioning_summary": "Missing HRIS passwordless UI run"},
    )
    assert response.status_code == 404


def test_submit_bulk_idp_provisioning_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    bulk_idp_provisioning_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/bulk-idp-provisioning/ui-runs/{ui_run_id}/start",
        headers=readonly_headers,
        json={"provisioning_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_bulk_idp_provisioning_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    bulk_idp_provisioning_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)
    api_client.post(
        f"/api/v1/enterprise/federation/bulk-idp-provisioning/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"provisioning_summary": "Listing test bulk IdP provisioning run"},
    )

    listing = api_client.get(
        "/api/v1/enterprise/federation/bulk-idp-provisioning/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
