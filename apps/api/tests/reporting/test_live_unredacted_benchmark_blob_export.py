"""Admin-gated live unredacted benchmark blob export integration tests."""

import uuid

import pytest
from fastapi.testclient import TestClient

from api.modules.documents.storage import (
    MemoryDocumentStorage,
    reset_document_storage,
    set_document_storage,
)


@pytest.fixture
def memory_document_storage() -> MemoryDocumentStorage:
    storage = MemoryDocumentStorage()
    set_document_storage(storage)
    yield storage
    reset_document_storage()


def _prepare_approved_unredacted_export(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    refresh = api_client.post(
        "/api/v1/reporting/cross-org-benchmarks/refresh",
        headers=admin_headers,
    )
    assert refresh.status_code == 200, refresh.text
    benchmark_run_id = refresh.json()["run"]["id"]

    submit = api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/benchmark-runs/{benchmark_run_id}/start",
        headers=admin_headers,
        json={"export_summary": "Parent unredacted export for blob pipeline"},
    )
    assert submit.status_code == 200, submit.text
    export_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/runs/{export_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "approved"
    return export_run_id


def test_live_unredacted_benchmark_blob_export_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    unredacted_cross_org_benchmark_export_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/live-unredacted-benchmark-blob-exports/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_live_unredacted_benchmark_blob_export_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    live_unredacted_benchmark_blob_export_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/live-unredacted-benchmark-blob-exports/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["unredacted_export_ready"] is True
    assert payload["blockers"] == []


def test_submit_live_blob_export_requires_approved_unredacted_export(
    api_client: TestClient,
    admin_headers: dict[str, str],
    live_unredacted_benchmark_blob_export_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/reporting/live-unredacted-benchmark-blob-exports/unredacted-export-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"export_summary": "Missing parent export"},
    )
    assert response.status_code == 404


def test_submit_and_approve_live_unredacted_benchmark_blob_export(
    api_client: TestClient,
    admin_headers: dict[str, str],
    live_unredacted_benchmark_blob_export_env: None,
    memory_document_storage: MemoryDocumentStorage,
) -> None:
    export_run_id = _prepare_approved_unredacted_export(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/reporting/live-unredacted-benchmark-blob-exports/unredacted-export-runs/{export_run_id}/start",
        headers=admin_headers,
        json={"export_summary": "Placeholder blob export after approved parent"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["unredacted_export_run_id"] == export_run_id
    assert run["storage_key"] is None

    approve = api_client.post(
        f"/api/v1/reporting/live-unredacted-benchmark-blob-exports/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    exported = approve.json()["run"]
    assert exported["status"] == "exported"
    assert exported["exported_at"] is not None
    assert exported["storage_key"] is not None
    assert exported["content_type"] == "application/json"
    assert exported["byte_size"] is not None and exported["byte_size"] > 0
    assert memory_document_storage.get_object(exported["storage_key"])


def test_submit_live_blob_export_forbidden_for_manager(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    live_unredacted_benchmark_blob_export_env: None,
) -> None:
    export_run_id = _prepare_approved_unredacted_export(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/reporting/live-unredacted-benchmark-blob-exports/unredacted-export-runs/{export_run_id}/start",
        headers=manager_headers,
        json={"export_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_live_unredacted_benchmark_blob_export_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    live_unredacted_benchmark_blob_export_env: None,
) -> None:
    export_run_id = _prepare_approved_unredacted_export(api_client, admin_headers)
    api_client.post(
        f"/api/v1/reporting/live-unredacted-benchmark-blob-exports/unredacted-export-runs/{export_run_id}/start",
        headers=admin_headers,
        json={"export_summary": "Listing test blob export run"},
    )

    listing = api_client.get(
        "/api/v1/reporting/live-unredacted-benchmark-blob-exports/runs",
        headers=manager_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
