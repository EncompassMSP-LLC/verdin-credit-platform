"""Admin-gated unredacted cross-org benchmark export integration tests."""

import uuid

from fastapi.testclient import TestClient


def _refresh_cross_org_benchmark(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    response = api_client.post(
        "/api/v1/reporting/cross-org-benchmarks/refresh",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    return response.json()["run"]["id"]


def test_unredacted_cross_org_benchmark_export_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    cross_org_benchmark_enabled: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/unredacted-cross-org-benchmark-exports/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_unredacted_cross_org_benchmark_export_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    unredacted_cross_org_benchmark_export_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/unredacted-cross-org-benchmark-exports/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["cross_org_benchmark_ready"] is True
    assert payload["blockers"] == []


def test_submit_unredacted_cross_org_benchmark_export_requires_completed_benchmark_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    unredacted_cross_org_benchmark_export_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/benchmark-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={
            "export_summary": "Attempt export before benchmark refresh",
            "export_reference_id": "missing-benchmark-run",
        },
    )
    assert response.status_code == 404


def test_submit_and_approve_unredacted_cross_org_benchmark_export_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    unredacted_cross_org_benchmark_export_env: None,
) -> None:
    benchmark_run_id = _refresh_cross_org_benchmark(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/benchmark-runs/{benchmark_run_id}/start",
        headers=admin_headers,
        json={
            "export_summary": "Unredacted benchmark export after completed refresh run",
            "export_reference_id": "governance-export-001",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["cross_org_benchmark_run_id"] == benchmark_run_id
    assert run["export_reference_id"] == "governance-export-001"

    approve = api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None
    assert approved["export_reference_id"] == "governance-export-001"


def test_submit_unredacted_cross_org_benchmark_export_forbidden_for_manager(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    unredacted_cross_org_benchmark_export_env: None,
) -> None:
    benchmark_run_id = _refresh_cross_org_benchmark(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/benchmark-runs/{benchmark_run_id}/start",
        headers=manager_headers,
        json={
            "export_summary": "Should not submit",
            "export_reference_id": "forbidden",
        },
    )
    assert response.status_code == 403


def test_list_unredacted_cross_org_benchmark_export_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    unredacted_cross_org_benchmark_export_env: None,
) -> None:
    benchmark_run_id = _refresh_cross_org_benchmark(api_client, admin_headers)
    api_client.post(
        f"/api/v1/reporting/unredacted-cross-org-benchmark-exports/benchmark-runs/{benchmark_run_id}/start",
        headers=admin_headers,
        json={
            "export_summary": "Listing test unredacted benchmark export run",
            "export_reference_id": "listing-test",
        },
    )

    listing = api_client.get(
        "/api/v1/reporting/unredacted-cross-org-benchmark-exports/runs",
        headers=manager_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
