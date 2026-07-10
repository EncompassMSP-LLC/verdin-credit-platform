"""Client portal document upload integration tests."""

import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.job_queue import JobMessage, JobType
from api.modules.documents.storage import (
    MemoryDocumentStorage,
    reset_document_storage,
    set_document_storage,
)
from tests.documents.conftest import sample_pdf_upload
from tests.helpers.client_payload import sample_client_payload


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(job_type=job_type, payload=payload or {}, job_id="test-ocr-job")


@pytest.fixture(autouse=True)
def mock_ocr_enqueue() -> Generator[None]:
    with patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue):
        yield


@pytest.fixture(autouse=True)
def memory_storage() -> Generator[MemoryDocumentStorage]:
    storage = MemoryDocumentStorage()
    reset_document_storage()
    set_document_storage(storage)
    yield storage
    reset_document_storage()


def _create_client(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    display_name: str,
    email: str | None = None,
) -> str:
    payload = sample_client_payload(display_name=display_name)
    if email:
        payload["email"] = email
    response = api_client.post("/api/v1/clients", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_portal_user(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
    *,
    email: str,
) -> dict:
    response = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _portal_login(api_client: TestClient, email: str) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_case(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    client_id: str,
) -> dict:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": title, "client_id": client_id},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_portal_document_upload_hidden_when_disabled(api_client: TestClient) -> None:
    get_feature_flags.cache_clear()
    response = api_client.post(
        f"/api/v1/portal/cases/{uuid.uuid4()}/documents",
        data={"title": "Evidence"},
        files={"file": ("report.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert response.status_code == 404


def test_portal_user_uploads_document_to_linked_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
    memory_storage: MemoryDocumentStorage,
) -> None:
    email = f"portal-upload-{uuid.uuid4().hex[:8]}@example.com"
    display_name = f"Upload Client {uuid.uuid4().hex[:6]}"
    client_id = _create_client(
        api_client,
        manager_headers,
        display_name=display_name,
        email=email,
    )
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    linked_case = _create_case(
        api_client,
        manager_headers,
        title="Upload Case",
        client_id=client_id,
    )

    portal_headers = _portal_login(api_client, email)
    filename, file_obj, content_type = sample_pdf_upload()
    upload_response = api_client.post(
        f"/api/v1/portal/cases/{linked_case['id']}/documents",
        headers=portal_headers,
        data={"title": "ID Copy", "description": "Driver license"},
        files={"file": (filename, file_obj, content_type)},
    )
    assert upload_response.status_code == 201, upload_response.text
    uploaded = upload_response.json()
    assert uploaded["title"] == "ID Copy"
    assert uploaded["case_id"] == linked_case["id"]
    assert uploaded["file_name"] == filename
    assert len(memory_storage._objects) == 1

    list_response = api_client.get(
        f"/api/v1/portal/cases/{linked_case['id']}/documents",
        headers=portal_headers,
    )
    assert list_response.status_code == 200, list_response.text
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == uploaded["id"]


def test_portal_user_cannot_upload_to_unlinked_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-blocked-upload-{uuid.uuid4().hex[:8]}@example.com"
    client_id = _create_client(api_client, manager_headers, display_name="Blocked Upload Client")
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    other_case = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "Private Case",
            "client_name": "Other Client",
            "client_email": f"private-{uuid.uuid4().hex[:8]}@example.com",
        },
    ).json()

    portal_headers = _portal_login(api_client, email)
    filename, file_obj, content_type = sample_pdf_upload()
    response = api_client.post(
        f"/api/v1/portal/cases/{other_case['id']}/documents",
        headers=portal_headers,
        data={"title": "Should Fail"},
        files={"file": (filename, file_obj, content_type)},
    )
    assert response.status_code == 404


def test_staff_can_see_portal_uploaded_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-staff-visible-{uuid.uuid4().hex[:8]}@example.com"
    client_id = _create_client(api_client, manager_headers, display_name="Staff Visible Client")
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    linked_case = _create_case(
        api_client,
        manager_headers,
        title="Shared Case",
        client_id=client_id,
    )

    portal_headers = _portal_login(api_client, email)
    filename, file_obj, content_type = sample_pdf_upload()
    upload_response = api_client.post(
        f"/api/v1/portal/cases/{linked_case['id']}/documents",
        headers=portal_headers,
        data={"title": "Portal Evidence"},
        files={"file": (filename, file_obj, content_type)},
    )
    assert upload_response.status_code == 201, upload_response.text
    document_id = upload_response.json()["id"]

    staff_response = api_client.get(
        f"/api/v1/documents/{document_id}",
        headers=manager_headers,
    )
    assert staff_response.status_code == 200, staff_response.text
    assert staff_response.json()["title"] == "Portal Evidence"
