"""Tests for bureau response ingestion audit scaffold (Version 16.0 slice 3)."""

from fastapi.testclient import TestClient


def test_bureau_response_ingestion_status(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/compliance/bureau-response-ingestion/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["enabled"] is True
    assert body["ready"] is False
    assert body["live_polling_enabled"] is False
    assert any("17.0" in blocker for blocker in body["blockers"])


def test_start_ingestion_run_records_deferred(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    start = api_client.post(
        "/api/v1/compliance/bureau-response-ingestion/runs",
        headers=manager_headers,
        json={
            "summary": "Operator requested Experian response check for case queue",
            "bureau_target": "experian",
        },
    )
    assert start.status_code == 201, start.text
    payload = start.json()
    assert payload["run"]["status"] == "deferred"
    assert "17.0" in payload["run"]["deferral_reason"]
    assert "no external bureau contact" in payload["run"]["deferral_reason"].lower()
    run_id = payload["run"]["id"]

    listed = api_client.get(
        "/api/v1/compliance/bureau-response-ingestion/runs",
        headers=manager_headers,
    )
    assert listed.status_code == 200, listed.text
    assert any(item["id"] == run_id for item in listed.json()["items"])

    detail = api_client.get(
        f"/api/v1/compliance/bureau-response-ingestion/runs/{run_id}",
        headers=manager_headers,
    )
    assert detail.status_code == 200, detail.text
    assert detail.json()["status"] == "deferred"


def test_start_ingestion_run_requires_write(
    api_client: TestClient,
    readonly_headers: dict[str, str],
) -> None:
    forbidden = api_client.post(
        "/api/v1/compliance/bureau-response-ingestion/runs",
        headers=readonly_headers,
        json={"summary": "Should be denied"},
    )
    assert forbidden.status_code == 403
