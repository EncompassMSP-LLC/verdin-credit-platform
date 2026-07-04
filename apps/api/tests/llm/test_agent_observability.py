"""Agent observability scaffold integration tests."""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.modules.auth.models import Organization
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.llm.agent_observability_models import AgentObservabilityKind


@pytest.fixture
def agent_observability_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_AI", "true")
    monkeypatch.setenv("ENABLE_AGENT_OBSERVABILITY", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def open_case(db_session: AsyncSession, test_org: Organization) -> Case:
    case = Case(
        organization_id=test_org.id,
        title="Agent observability case",
        client_name="Observability Client",
        status=CaseStatus.OPEN,
        stage=CaseStage.INTAKE,
        priority=CasePriority.MEDIUM,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


def test_agent_observability_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/llm/agents/status", headers=manager_headers)
    assert response.status_code == 404


def test_agent_observability_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_observability_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/agents/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["ai_enabled"] is True
    assert payload["blockers"] == []


def test_run_agent_observability_without_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_observability_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/agents/run",
        headers=manager_headers,
        json={"agent_kind": AgentObservabilityKind.CASE_REVIEW.value},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["run"]["steps_completed"] == 1
    assert payload["run"]["steps_failed"] == 0
    assert payload["run"]["timeline_event_id"] is None


def test_run_agent_observability_with_case_creates_timeline_event(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_observability_env: None,
    open_case: Case,
) -> None:
    response = api_client.post(
        "/api/v1/llm/agents/run",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.CASE_REVIEW.value,
            "case_id": str(open_case.id),
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["run"]["case_id"] == str(open_case.id)
    assert payload["run"]["timeline_event_id"] is not None

    timeline = api_client.get(
        f"/api/v1/timeline?case_id={open_case.id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "agent_observability_run" for event in events)


def test_run_agent_observability_unknown_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_observability_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/agents/run",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.CASE_REVIEW.value,
            "case_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 404
    assert "Case not found" in response.json()["detail"]


def test_run_agent_observability_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    agent_observability_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/agents/run",
        headers=readonly_headers,
        json={"agent_kind": AgentObservabilityKind.CASE_REVIEW.value},
    )
    assert response.status_code == 403


def test_list_agent_observability_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_observability_env: None,
) -> None:
    api_client.post(
        "/api/v1/llm/agents/run",
        headers=manager_headers,
        json={"agent_kind": AgentObservabilityKind.DOCUMENT_TRIAGE.value},
    )
    response = api_client.get("/api/v1/llm/agents/runs", headers=manager_headers)
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
