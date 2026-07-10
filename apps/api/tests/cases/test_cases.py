"""Case management endpoint tests."""

import uuid

from fastapi.testclient import TestClient

from tests.helpers.client_payload import sample_client_payload


def test_create_case(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "New Credit Review",
            "client_name": "Jane Client",
            "client_email": "jane@example.com",
            "priority": "high",
            "stage": "intake",
            "status": "open",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Credit Review"
    assert data["client_name"] == "Jane Client"
    assert data["status"] == "open"
    assert data["priority"] == "high"


def test_create_case_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/cases",
        headers=readonly_headers,
        json={
            "title": "Blocked Case",
            "client_name": "Jane Client",
        },
    )
    assert response.status_code == 403


def test_list_cases(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "List Test Case", "client_name": "List Client"},
    )
    response = api_client.get("/api/v1/cases", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["page"] == 1


def test_list_cases_search_filter(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    unique = f"SearchClient-{uuid.uuid4().hex[:6]}"
    api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Searchable Case", "client_name": unique},
    )
    response = api_client.get(
        "/api/v1/cases",
        headers=manager_headers,
        params={"search": unique},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    assert any(item["client_name"] == unique for item in response.json()["items"])


def test_get_case(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Detail Case", "client_name": "Detail Client"},
    )
    case_id = create.json()["id"]
    response = api_client.get(f"/api/v1/cases/{case_id}", headers=manager_headers)
    assert response.status_code == 200
    assert response.json()["id"] == case_id


def test_get_case_not_found(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    response = api_client.get(f"/api/v1/cases/{uuid.uuid4()}", headers=manager_headers)
    assert response.status_code == 404


def test_update_case(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Original Title", "client_name": "Update Client"},
    )
    case_id = create.json()["id"]
    response = api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"title": "Updated Title", "status": "active", "priority": "critical"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "active"
    assert data["priority"] == "critical"


def test_delete_case(api_client: TestClient, auth_headers: dict[str, str]) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={"title": "Delete Me", "client_name": "Delete Client"},
    )
    case_id = create.json()["id"]
    delete = api_client.delete(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert delete.status_code == 204
    get_response = api_client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_case_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    auth_headers: dict[str, str],
) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Protected Delete", "client_name": "Protected Client"},
    )
    case_id = create.json()["id"]
    response = api_client.delete(f"/api/v1/cases/{case_id}", headers=manager_headers)
    assert response.status_code == 403


def test_cases_require_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/cases")
    assert response.status_code == 401


def test_create_case_with_client_id(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_response = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(
            display_name="Linked Client",
            email="linked@example.com",
        ),
    )
    assert client_response.status_code == 201
    client_id = client_response.json()["id"]

    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "Linked Case",
            "client_id": client_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["client_id"] == client_id
    assert data["client_name"] == "Linked Client"
    assert data["client_email"] == "linked@example.com"


def test_create_case_rejects_foreign_client_id(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "Invalid Link",
            "client_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 422


def test_list_cases_filter_by_client_id(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_response = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Filter Client"),
    )
    assert client_response.status_code == 201
    client_id = client_response.json()["id"]

    linked = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Filter Match", "client_id": client_id},
    )
    assert linked.status_code == 201

    api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Filter Miss", "client_name": "Other Client"},
    )

    response = api_client.get(
        "/api/v1/cases",
        headers=manager_headers,
        params={"client_id": client_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == linked.json()["id"]
