"""Dashboard API integration tests."""

from fastapi.testclient import TestClient


def test_dashboard_requires_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/dashboard")
    assert response.status_code == 401


def test_dashboard_returns_mission_control_snapshot(
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

    for section in (
        "overview",
        "cases",
        "accounts",
        "documents",
        "timeline",
        "tasks",
        "processing",
        "performance",
        "alerts",
    ):
        assert section in body

    assert body["overview"]["open_cases"] >= 1
    assert body["cases"]["open"] >= 1
    assert isinstance(body["timeline"], list)
    assert isinstance(body["alerts"]["items"], list)
    assert body["alerts"]["total"] == len(body["alerts"]["items"])


def test_dashboard_readable_by_read_only_user(
    api_client: TestClient,
    readonly_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/dashboard", headers=readonly_headers)
    assert response.status_code == 200, response.text
    assert "overview" in response.json()
