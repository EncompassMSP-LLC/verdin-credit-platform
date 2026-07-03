"""Retention enforcement job tests."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.modules.cases.models import Case, CaseStatus
from api.modules.clients.models import Client
from api.modules.documents.models import Document


@pytest.fixture
def enforcement_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_COMPLIANCE_ENFORCEMENT", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def test_enforcement_endpoints_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/compliance/enforcement/status", headers=admin_headers)
    assert response.status_code == 404


def test_enforcement_status_when_enabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enforcement_enabled: None,
) -> None:
    response = api_client.get("/api/v1/compliance/enforcement/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["enabled"] is True
    assert data["active_policy_count"] == 0
    assert data["last_run_at"] is None


def test_run_enforcement_requires_admin(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enforcement_enabled: None,
) -> None:
    response = api_client.post("/api/v1/compliance/enforcement/run", headers=manager_headers)
    assert response.status_code == 403


@pytest.fixture
async def expired_document(
    db_session: AsyncSession,
    test_client: Client,
) -> Document:
    now = datetime.now(UTC)
    created_at = now - timedelta(days=60)
    case = Case(
        id=uuid.uuid4(),
        organization_id=test_client.organization_id,
        client_id=test_client.id,
        title="Retention test case",
        client_name=test_client.display_name,
        status=CaseStatus.OPEN,
        opened_at=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(case)
    await db_session.flush()

    document = Document(
        id=uuid.uuid4(),
        organization_id=test_client.organization_id,
        case_id=case.id,
        title="Expired document",
        file_name="expired.pdf",
        storage_key=f"org/{test_client.organization_id}/expired.pdf",
        file_hash=uuid.uuid4().hex,
        created_at=created_at,
        updated_at=created_at,
    )
    db_session.add(document)
    await db_session.commit()
    return document


def test_run_enforcement_soft_deletes_expired_documents(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enforcement_enabled: None,
    expired_document: Document,
) -> None:
    policy_response = api_client.post(
        "/api/v1/compliance/retention-policies",
        headers=admin_headers,
        json={
            "name": "Short document retention",
            "scope": "documents",
            "retention_days": 30,
        },
    )
    assert policy_response.status_code == 201, policy_response.text

    run_response = api_client.post("/api/v1/compliance/enforcement/run", headers=admin_headers)
    assert run_response.status_code == 200, run_response.text
    result = run_response.json()
    assert result["policies_processed"] == 1
    assert result["items_enforced"] >= 1
    assert len(result["runs"]) == 1
    assert result["runs"][0]["status"] == "completed"
    assert result["runs"][0]["scope"] == "documents"

    runs_response = api_client.get("/api/v1/compliance/enforcement/runs", headers=admin_headers)
    assert runs_response.status_code == 200
    assert runs_response.json()["total"] >= 1

    status_response = api_client.get("/api/v1/compliance/enforcement/status", headers=admin_headers)
    assert status_response.status_code == 200
    assert status_response.json()["last_run_at"] is not None

    _ = expired_document


def test_run_enforcement_skips_audit_logs_policy(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enforcement_enabled: None,
) -> None:
    policy_response = api_client.post(
        "/api/v1/compliance/retention-policies",
        headers=admin_headers,
        json={
            "name": "Audit log placeholder",
            "scope": "audit_logs",
            "retention_days": 365,
        },
    )
    assert policy_response.status_code == 201, policy_response.text

    run_response = api_client.post("/api/v1/compliance/enforcement/run", headers=admin_headers)
    assert run_response.status_code == 200, run_response.text
    result = run_response.json()
    assert result["policies_processed"] == 1
    assert result["items_enforced"] == 0
    assert result["runs"][0]["status"] == "skipped"
    assert result["runs"][0]["error_message"] is not None
