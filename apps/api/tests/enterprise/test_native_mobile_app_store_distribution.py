"""Admin-gated native mobile app store distribution integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.enterprise.test_native_mobile_passkey_client import (
    _prepare_approved_mobile_passkey_readiness_run,
)


def _prepare_approved_native_mobile_passkey_client_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    readiness_run_id = _prepare_approved_mobile_passkey_readiness_run(api_client, admin_headers)
    submit = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{readiness_run_id}/start",
        headers=admin_headers,
        json={
            "client_summary": "Parent native passkey client for app store distribution",
            "platform": "ios",
        },
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    approve = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "approved"
    return run_id


def test_native_mobile_app_store_distribution_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_passkey_client_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/native-mobile-app-store-distribution/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_native_mobile_app_store_distribution_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_app_store_distribution_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/native-mobile-app-store-distribution/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["native_mobile_passkey_client_ready"] is True
    assert payload["blockers"] == []


def test_submit_app_store_distribution_requires_approved_passkey_client_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_app_store_distribution_env: None,
) -> None:
    readiness_run_id = _prepare_approved_mobile_passkey_readiness_run(api_client, admin_headers)
    submit_parent = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-passkey-client/readiness-runs/{readiness_run_id}/start",
        headers=admin_headers,
        json={
            "client_summary": "Pending — cannot start app store distribution yet",
            "platform": "android",
        },
    )
    assert submit_parent.status_code == 200, submit_parent.text
    pending_run_id = submit_parent.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-app-store-distribution/passkey-client-runs/{pending_run_id}/start",
        headers=admin_headers,
        json={
            "distribution_summary": "Attempt distribution before passkey client approved",
            "store_target": "play_store",
        },
    )
    assert response.status_code == 409
    assert "not approved" in response.json()["detail"]


def test_submit_and_approve_native_mobile_app_store_distribution_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_app_store_distribution_env: None,
) -> None:
    client_run_id = _prepare_approved_native_mobile_passkey_client_run(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-app-store-distribution/passkey-client-runs/{client_run_id}/start",
        headers=admin_headers,
        json={
            "distribution_summary": "App store distribution readiness after approved passkey client",
            "store_target": "app_store",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["native_mobile_passkey_client_run_id"] == client_run_id
    assert run["platform"] == "ios"
    assert run["store_target"] == "app_store"

    approve = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-app-store-distribution/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    ready = approve.json()["run"]
    assert ready["status"] == "ready"
    assert ready["ready_at"] is not None
    assert ready["approved_at"] is not None


def test_submit_app_store_distribution_unknown_passkey_client_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_app_store_distribution_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-app-store-distribution/passkey-client-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={
            "distribution_summary": "Missing native mobile passkey client run",
            "store_target": "app_store",
        },
    )
    assert response.status_code == 404


def test_submit_app_store_distribution_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    native_mobile_app_store_distribution_env: None,
) -> None:
    client_run_id = _prepare_approved_native_mobile_passkey_client_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-app-store-distribution/passkey-client-runs/{client_run_id}/start",
        headers=readonly_headers,
        json={"distribution_summary": "Should not submit", "store_target": "app_store"},
    )
    assert response.status_code == 403


def test_list_native_mobile_app_store_distribution_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    native_mobile_app_store_distribution_env: None,
) -> None:
    client_run_id = _prepare_approved_native_mobile_passkey_client_run(api_client, admin_headers)
    api_client.post(
        f"/api/v1/enterprise/federation/native-mobile-app-store-distribution/passkey-client-runs/{client_run_id}/start",
        headers=admin_headers,
        json={
            "distribution_summary": "List test native mobile app store distribution run",
            "store_target": "app_store",
        },
    )

    listing = api_client.get(
        "/api/v1/enterprise/federation/native-mobile-app-store-distribution/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
