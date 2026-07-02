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
        "operations",
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


def test_dashboard_aggregates_cases_accounts_tasks_and_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Aggregate Case", "client_name": "Aggregate Client"},
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]

    account_response = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json={
            "case_id": case_id,
            "bureau": "experian",
            "creditor_name": "Aggregate Bank",
            "account_status": "open",
            "payment_status": "current",
            "balance": "250.00",
        },
    )
    assert account_response.status_code == 201, account_response.text

    task_response = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "Aggregate Task", "case_id": case_id, "priority": "high"},
    )
    assert task_response.status_code == 201, task_response.text

    response = api_client.get("/api/v1/dashboard", headers=manager_headers)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["overview"]["open_cases"] >= 1
    assert body["overview"]["active_accounts"] >= 1
    assert body["accounts"]["total"] >= 1
    assert body["tasks"]["pending"] >= 1
    assert any(item["event_type"] == "TASK_CREATED" for item in body["timeline"])
