"""Dashboard API integration tests."""

from fastapi.testclient import TestClient


def test_dashboard_requires_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/dashboard")
    assert response.status_code == 401


def test_dashboard_returns_aggregated_snapshot(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Dashboard Case", "client_name": "Dashboard Client", "priority": "high"},
    )
    assert case_response.status_code == 201, case_response.text

    response = api_client.get("/api/v1/dashboard", headers=manager_headers)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["refresh_seconds"] == 30
    assert "generated_at" in body

    for section in ("kpis", "processing", "tasks", "timeline", "ai", "performance"):
        assert section in body

    assert body["kpis"]["open_cases"] >= 1
    assert isinstance(body["tasks"]["overdue_tasks"], list)
    assert isinstance(body["timeline"], list)
    assert body["ai"]["entity_resolution_rate"] >= 0
    assert body["performance"]["resolution_rate"] >= 0


def test_dashboard_readable_by_read_only_user(
    api_client: TestClient,
    readonly_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/dashboard", headers=readonly_headers)
    assert response.status_code == 200, response.text
    assert "kpis" in response.json()
