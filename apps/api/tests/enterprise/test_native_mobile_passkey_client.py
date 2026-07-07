"""Admin-gated native mobile passkey client integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_bulk_idp_provisioning import _prepare_approved_hris_passwordless_ui_run


def _prepare_approved_mobile_passkey_readiness_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"readiness_summary": "Passkey readiness before native mobile client scaffold"},
    )
    assert submit.status_code == 200, submit.text
    readiness_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/runs/{readiness_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "approved"
    return readiness_run_id


def test_native_mobile_passkey_client_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    mobile_passkey_readiness_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/native-mobile-passkey-client/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_native_mobile_passkey_client_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/native-mobile-passkey-client/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["mobile_passkey_readiness_ready"] is True
    assert payload["blockers"] == []


def test_submit_native_mobile_passkey_client_requires_approved_readiness_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    ui_run_id = _prepare_approved_hris_passwordless_ui_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/mobile-passkey-readiness/ui-runs/{ui_run_id}/start",
        headers=admin_headers,
        json={"readiness_summary": "Pending approval — cannot start native client yet"},
    )
    assert submit.status_code == 200, submit.text
    readiness_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{readiness_run_id}/start",
        headers=admin_headers,
        json={
            "client_summary": "Attempt native client before passkey readiness approved",
            "platform": "ios",
        },
    )
    assert response.status_code == 409
    assert "not approved" in response.json()["detail"]


def test_submit_and_approve_native_mobile_passkey_client_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    readiness_run_id = _prepare_approved_mobile_passkey_readiness_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{readiness_run_id}/start",
        headers=admin_headers,
        json={
            "client_summary": "Native mobile passkey client after approved readiness",
            "platform": "android",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["mobile_passkey_readiness_run_id"] == readiness_run_id
    assert run["platform"] == "android"

    approve = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None


def test_submit_native_mobile_passkey_client_unknown_readiness_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"client_summary": "Missing passkey readiness run", "platform": "ios"},
    )
    assert response.status_code == 404


def test_submit_native_mobile_passkey_client_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    readiness_run_id = _prepare_approved_mobile_passkey_readiness_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{readiness_run_id}/start",
        headers=readonly_headers,
        json={"client_summary": "Should not submit", "platform": "ios"},
    )
    assert response.status_code == 403


def test_list_native_mobile_passkey_client_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    readiness_run_id = _prepare_approved_mobile_passkey_readiness_run(api_client, admin_headers)
    api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{readiness_run_id}/start",
        headers=admin_headers,
        json={
            "client_summary": "Listing test native mobile passkey client run",
            "platform": "ios",
        },
    )

    listing = api_client.get(
        "/api/v1/enterprise/federation/native-mobile-passkey-client/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
