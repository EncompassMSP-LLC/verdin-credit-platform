"""Timeline endpoint integration tests."""

from fastapi.testclient import TestClient

from tests.documents.conftest import sample_pdf_upload


def test_case_create_emits_timeline_event(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Timeline Case", "client_name": "Timeline Client"},
    )
    assert create.status_code == 201, create.text
    case_id = create.json()["id"]

    response = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"case_id": case_id, "event_type": "CASE_CREATED"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["event_type"] == "CASE_CREATED"
    assert data["items"][0]["case_id"] == case_id


def test_document_upload_emits_timeline_event(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Timeline Doc", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert create.status_code == 201, create.text
    document_id = create.json()["id"]

    response = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"document_id": document_id, "event_type": "DOCUMENT_UPLOADED"},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_login_emits_timeline_event(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"event_type": "USER_LOGIN", "event_category": "auth"},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_case_timeline_preserves_event_sequence(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Sequenced Case", "client_name": "Sequence Client"},
    )
    assert create.status_code == 201, create.text
    case_id = create.json()["id"]

    update = api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"title": "Sequenced Case Updated"},
    )
    assert update.status_code == 200, update.text

    response = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"case_id": case_id, "sort_order": "asc"},
    )
    assert response.status_code == 200, response.text
    event_types = [item["event_type"] for item in response.json()["items"]]
    assert event_types[:2] == ["CASE_CREATED", "CASE_UPDATED"]
