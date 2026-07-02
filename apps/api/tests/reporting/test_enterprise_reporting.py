"""Enterprise reporting read model tests."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from api.core.enterprise_reporting import get_enterprise_reporting_status
from api.modules.auth.models import User


def _create_case(api_client: TestClient, headers: dict[str, str], *, title: str) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": title, "client_name": "Reporting Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_account(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    case_id: str,
    bureau: str,
) -> str:
    response = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json={
            "case_id": case_id,
            "creditor_name": f"{bureau.title()} Creditor",
            "bureau": bureau,
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "current",
            "dispute_status": "dispute_sent",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_task(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    case_id: str,
    assigned_user_id: str,
    title: str,
) -> str:
    response = api_client.post(
        "/api/v1/tasks",
        headers=headers,
        json={
            "title": title,
            "case_id": case_id,
            "assigned_user_id": assigned_user_id,
            "status": "open",
            "priority": "medium",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_enterprise_reporting_status_payload() -> None:
    status = get_enterprise_reporting_status()
    assert status.enterprise_reporting_enabled is True
    assert "bureau_performance_by_tradeline" in status.capabilities


def test_get_enterprise_reporting_status(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/reporting/status", headers=manager_headers)
    assert response.status_code == 200
    assert response.json()["enterprise_reporting_enabled"] is True


def test_bureau_performance_reporting(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_id = _create_case(api_client, manager_headers, title="Bureau Reporting Case")
    _create_account(api_client, manager_headers, case_id=case_id, bureau="equifax")
    _create_account(api_client, manager_headers, case_id=case_id, bureau="experian")

    response = api_client.get("/api/v1/reporting/bureau-performance", headers=manager_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert "generated_at" in body
    performance = body["bureau_performance"]
    assert performance["total_accounts"] >= 2
    bureaus = {item["bureau"]: item for item in performance["bureaus"]}
    assert bureaus["equifax"]["total_accounts"] >= 1
    assert bureaus["experian"]["total_accounts"] >= 1
    assert "dispute_sent" in bureaus["equifax"]["dispute_status"]


def test_team_productivity_reporting(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    case_id = _create_case(api_client, manager_headers, title="Productivity Case")
    _create_task(
        api_client,
        manager_headers,
        case_id=case_id,
        assigned_user_id=str(case_manager_user.id),
        title="Open productivity task",
    )

    complete_response = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={
            "title": "Completed productivity task",
            "case_id": case_id,
            "assigned_user_id": str(case_manager_user.id),
            "status": "completed",
            "priority": "medium",
            "completed_at": datetime.now(UTC).isoformat(),
        },
    )
    assert complete_response.status_code == 201, complete_response.text
    task_id = complete_response.json()["id"]
    patch_response = api_client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=manager_headers,
        json={"status": "completed"},
    )
    assert patch_response.status_code == 200, patch_response.text

    api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={
            "assigned_to_id": str(case_manager_user.id),
            "status": "closed",
            "closed_at": datetime.now(UTC).isoformat(),
        },
    )

    response = api_client.get("/api/v1/reporting/team-productivity", headers=manager_headers)
    assert response.status_code == 200, response.text
    productivity = response.json()["team_productivity"]
    member = next(
        (item for item in productivity["members"] if item["user_id"] == str(case_manager_user.id)),
        None,
    )
    assert member is not None
    assert member["open_tasks"] >= 1
    assert productivity["open_tasks_total"] >= 1
