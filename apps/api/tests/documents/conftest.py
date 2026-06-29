"""Fixtures for document management integration tests."""

import io
import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register all ORM mappers
from api.core.constants import UserRole
from api.core.job_queue import JobMessage, JobType
from api.core.security import hash_password
from api.modules.auth.models import Organization, User
from api.modules.documents.storage import (
    MemoryDocumentStorage,
    reset_document_storage,
    set_document_storage,
)


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


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        slug=f"test-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def case_manager_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"manager-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="Manager",
        role=UserRole.CASE_MANAGER,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def owner_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"owner-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="Owner",
        role=UserRole.OWNER,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


def _login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


@pytest.fixture
def auth_headers(api_client: TestClient, owner_user: User) -> dict[str, str]:
    return _login(api_client, owner_user.email)


@pytest.fixture
def sample_case_id(api_client: TestClient, manager_headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Document Test Case", "client_name": "Doc Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def sample_pdf_upload() -> tuple[str, io.BytesIO, str]:
    content = b"%PDF-1.4 sample credit report content for testing"
    return ("report.pdf", io.BytesIO(content), "application/pdf")
