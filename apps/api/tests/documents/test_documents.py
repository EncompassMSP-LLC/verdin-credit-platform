"""Document foundation endpoint tests."""

import uuid

from fastapi.testclient import TestClient

from tests.documents.conftest import sample_pdf_upload


def test_upload_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    memory_storage,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    response = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Credit Report", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == "Credit Report"
    assert data["case_id"] == sample_case_id
    assert data["file_hash"]
    assert data["is_duplicate"] is False
    assert len(memory_storage._objects) == 1


def test_duplicate_detection(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    for title in ("Original Report", "Duplicate Report"):
        filename, file_obj, content_type = sample_pdf_upload()
        response = api_client.post(
            "/api/v1/documents",
            headers=manager_headers,
            data={"title": title, "case_id": sample_case_id},
            files={"file": (filename, file_obj, content_type)},
        )
        assert response.status_code == 201, response.text

    second = response.json()
    assert second["is_duplicate"] is True
    assert second["duplicate_of_id"] is not None


def test_list_documents(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Listed Doc", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    response = api_client.get("/api/v1/documents", headers=manager_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Detail Doc", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    response = api_client.get(f"/api/v1/documents/{document_id}", headers=manager_headers)
    assert response.status_code == 200
    assert len(response.json()["versions"]) == 1


def test_download_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Download Doc", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    response = api_client.get(
        f"/api/v1/documents/{document_id}/download",
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert b"PDF" in response.content


def test_upload_new_version(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Versioned Doc", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]

    updated_content = b"%PDF-1.4 updated version content"
    response = api_client.post(
        f"/api/v1/documents/{document_id}/versions",
        headers=manager_headers,
        files={"file": ("report-v2.pdf", updated_content, "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["version_number"] == 2


def test_update_document_metadata(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Old Title", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    response = api_client.patch(
        f"/api/v1/documents/{document_id}",
        headers=manager_headers,
        json={"title": "New Title", "description": "Updated description"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_document(
    api_client: TestClient,
    auth_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={"title": "Delete Me", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    delete = api_client.delete(f"/api/v1/documents/{document_id}", headers=auth_headers)
    assert delete.status_code == 204
    get_response = api_client.get(f"/api/v1/documents/{document_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_documents_require_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/documents")
    assert response.status_code == 401


def test_get_document_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(f"/api/v1/documents/{uuid.uuid4()}", headers=manager_headers)
    assert response.status_code == 404
