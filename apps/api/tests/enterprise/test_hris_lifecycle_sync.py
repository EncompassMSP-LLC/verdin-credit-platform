"""Admin-gated HRIS lifecycle sync integration tests."""

import uuid

from fastapi.testclient import TestClient

from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunKind
from tests.enterprise.conftest import VALID_SAML_METADATA


def _prepare_completed_hris_sync_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    upload = api_client.post(
        "/api/v1/enterprise/federation/saml-metadata/upload",
        headers=admin_headers,
        json={
            "metadata_xml": VALID_SAML_METADATA,
            "provider_key": "workday-hris",
        },
    )
    assert upload.status_code == 200, upload.text

    sync = api_client.post(
        "/api/v1/enterprise/federation/hris-sync/run",
        headers=admin_headers,
        json={"run_kind": HrisBidirectionalSyncRunKind.EMPLOYEES_INBOUND.value},
    )
    assert sync.status_code == 200, sync.text
    sync_run_id = sync.json()["run"]["id"]
    assert sync.json()["run"]["status"] == "completed"
    return sync_run_id


def test_hris_lifecycle_sync_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_sync_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-lifecycle/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_hris_lifecycle_sync_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_lifecycle_sync_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/enterprise/federation/hris-lifecycle/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["hris_sync_ready"] is True
    assert payload["blockers"] == []


def test_submit_hris_lifecycle_sync_requires_completed_bidirectional_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_lifecycle_sync_env: None,
) -> None:
    sync = api_client.post(
        "/api/v1/enterprise/federation/hris-sync/run",
        headers=admin_headers,
        json={"run_kind": HrisBidirectionalSyncRunKind.EMPLOYEES_INBOUND.value},
    )
    assert sync.status_code == 404

    listing = api_client.get(
        "/api/v1/enterprise/federation/hris-sync/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    failed_runs = [run for run in listing.json()["items"] if run["status"] == "failed"]
    assert failed_runs
    sync_run_id = failed_runs[0]["id"]

    response = api_client.post(
        f"/api/v1/enterprise/federation/hris-lifecycle/sync-runs/{sync_run_id}/start",
        headers=admin_headers,
        json={"lifecycle_summary": "Cannot start lifecycle from failed sync run"},
    )
    assert response.status_code == 409
    assert "not completed" in response.json()["detail"]


def test_submit_and_approve_hris_lifecycle_sync_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_lifecycle_sync_env: None,
) -> None:
    sync_run_id = _prepare_completed_hris_sync_run(api_client, admin_headers)

    start = api_client.post(
        f"/api/v1/enterprise/federation/hris-lifecycle/sync-runs/{sync_run_id}/start",
        headers=admin_headers,
        json={
            "lifecycle_summary": "Employee onboarding lifecycle sync after HRIS bidirectional run"
        },
    )
    assert start.status_code == 200, start.text
    run = start.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["hris_bidirectional_sync_run_id"] == sync_run_id
    assert run["run_kind"] == "employees_inbound"

    approve = api_client.post(
        f"/api/v1/enterprise/federation/hris-lifecycle/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "completed"
    assert approved["completed_at"] is not None


def test_start_hris_lifecycle_sync_unknown_bidirectional_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_lifecycle_sync_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/enterprise/federation/hris-lifecycle/sync-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"lifecycle_summary": "Missing HRIS bidirectional sync run"},
    )
    assert response.status_code == 404


def test_submit_hris_lifecycle_sync_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    hris_lifecycle_sync_env: None,
) -> None:
    sync_run_id = _prepare_completed_hris_sync_run(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/enterprise/federation/hris-lifecycle/sync-runs/{sync_run_id}/start",
        headers=readonly_headers,
        json={"lifecycle_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_hris_lifecycle_sync_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    hris_lifecycle_sync_env: None,
) -> None:
    sync_run_id = _prepare_completed_hris_sync_run(api_client, admin_headers)
    api_client.post(
        f"/api/v1/enterprise/federation/hris-lifecycle/sync-runs/{sync_run_id}/start",
        headers=admin_headers,
        json={"lifecycle_summary": "Listing test HRIS lifecycle sync run"},
    )

    response = api_client.get(
        "/api/v1/enterprise/federation/hris-lifecycle/runs",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
