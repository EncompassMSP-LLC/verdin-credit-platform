"""Task management endpoint tests."""

import uuid

from fastapi.testclient import TestClient


def test_create_task(
    api_client: TestClient, manager_headers: dict[str, str], sample_case_id: str
) -> None:
    response = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={
            "title": "Review documents",
            "description": "Check uploaded credit reports",
            "priority": "high",
            "case_id": sample_case_id,
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == "Review documents"
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert data["case_id"] == sample_case_id


def test_create_task_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    response = api_client.post(
        "/api/v1/tasks",
        headers=readonly_headers,
        json={"title": "Blocked", "case_id": sample_case_id},
    )
    assert response.status_code == 403


def test_list_tasks(
    api_client: TestClient, manager_headers: dict[str, str], sample_case_id: str
) -> None:
    api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "List Task", "case_id": sample_case_id},
    )
    response = api_client.get("/api/v1/tasks", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "items" in data


def test_list_tasks_overdue_filter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    overdue_due_date: str,
) -> None:
    api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={
            "title": "Overdue Task",
            "case_id": sample_case_id,
            "due_date": overdue_due_date,
        },
    )
    response = api_client.get(
        "/api/v1/tasks",
        headers=manager_headers,
        params={"overdue": True},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    assert any(item["title"] == "Overdue Task" for item in response.json()["items"])


def test_get_task(
    api_client: TestClient, manager_headers: dict[str, str], sample_case_id: str
) -> None:
    create = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "Get Task", "case_id": sample_case_id},
    )
    task_id = create.json()["id"]
    response = api_client.get(f"/api/v1/tasks/{task_id}", headers=manager_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(
    api_client: TestClient, manager_headers: dict[str, str], sample_case_id: str
) -> None:
    create = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "Before Update", "case_id": sample_case_id},
    )
    task_id = create.json()["id"]
    response = api_client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=manager_headers,
        json={"title": "After Update", "status": "in_progress"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "After Update"
    assert response.json()["status"] == "in_progress"


def test_complete_and_reopen_task(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "Complete Me", "case_id": sample_case_id},
    )
    task_id = create.json()["id"]

    complete = api_client.post(f"/api/v1/tasks/{task_id}/complete", headers=manager_headers)
    assert complete.status_code == 200
    assert complete.json()["status"] == "completed"
    assert complete.json()["completed_at"] is not None

    reopen = api_client.post(f"/api/v1/tasks/{task_id}/reopen", headers=manager_headers)
    assert reopen.status_code == 200
    assert reopen.json()["status"] == "open"
    assert reopen.json()["completed_at"] is None


def test_delete_task_requires_admin(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "Delete Me", "case_id": sample_case_id},
    )
    task_id = create.json()["id"]

    forbidden = api_client.delete(f"/api/v1/tasks/{task_id}", headers=manager_headers)
    assert forbidden.status_code == 403

    deleted = api_client.delete(f"/api/v1/tasks/{task_id}", headers=admin_headers)
    assert deleted.status_code == 204

    missing = api_client.get(f"/api/v1/tasks/{task_id}", headers=admin_headers)
    assert missing.status_code == 404


def test_task_create_emits_timeline_event(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": "Timeline Task", "case_id": sample_case_id},
    )
    assert create.status_code == 201
    task_id = create.json()["id"]

    response = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"event_type": "TASK_CREATED", "case_id": sample_case_id},
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["metadata"].get("title") == "Timeline Task" for item in items)
    assert any(item.get("case_id") == sample_case_id for item in items)

    complete = api_client.post(f"/api/v1/tasks/{task_id}/complete", headers=manager_headers)
    assert complete.status_code == 200

    completed_events = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"event_type": "TASK_COMPLETED", "case_id": sample_case_id},
    )
    assert completed_events.status_code == 200
    assert completed_events.json()["total"] >= 1


def test_complete_task_conflict_when_already_completed(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/tasks",
        headers=manager_headers,
        json={"title": f"Conflict-{uuid.uuid4().hex[:6]}", "case_id": sample_case_id},
    )
    task_id = create.json()["id"]
    api_client.post(f"/api/v1/tasks/{task_id}/complete", headers=manager_headers)
    again = api_client.post(f"/api/v1/tasks/{task_id}/complete", headers=manager_headers)
    assert again.status_code == 409
