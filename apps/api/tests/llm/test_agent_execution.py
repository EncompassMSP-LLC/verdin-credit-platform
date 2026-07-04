"""Human-gated agent execution scaffold integration tests."""

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
def agent_execution_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_AI", "true")
    monkeypatch.setenv("ENABLE_AGENT_OBSERVABILITY", "true")
    monkeypatch.setenv("ENABLE_AGENT_EXECUTION", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def open_case(db_session: AsyncSession, test_org: Organization) -> Case:
    case = Case(
        organization_id=test_org.id,
        title="Agent execution case",
        client_name="Execution Client",
        status=CaseStatus.OPEN,
        stage=CaseStage.INTAKE,
        priority=CasePriority.MEDIUM,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


def test_agent_execution_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/llm/execution/status", headers=manager_headers)
    assert response.status_code == 404


def test_agent_execution_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_execution_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/execution/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["observability_ready"] is True
    assert payload["blockers"] == []


def test_submit_agent_execution_step(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_execution_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/execution/steps",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.CASE_REVIEW.value,
            "step_summary": "Review dispute readiness for staff approval.",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["step"]["status"] == "pending_approval"
    assert payload["step"]["step_summary"].startswith("Review dispute")


def test_submit_and_approve_agent_execution_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_execution_env: None,
    open_case: Case,
) -> None:
    submit = api_client.post(
        "/api/v1/llm/execution/steps",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.DISPUTE_PREP.value,
            "step_summary": "Prepare dispute package after human review.",
            "case_id": str(open_case.id),
        },
    )
    assert submit.status_code == 200, submit.text
    step_id = submit.json()["step"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/execution/steps/{step_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["step"]
    assert approved["status"] == "executed"
    assert approved["timeline_event_id"] is not None

    timeline = api_client.get(
        f"/api/v1/timeline?case_id={open_case.id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "agent_execution_step" for event in events)


def test_submit_agent_execution_unknown_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_execution_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/execution/steps",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.CASE_REVIEW.value,
            "step_summary": "Missing case",
            "case_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 404
    assert "Case not found" in response.json()["detail"]


def test_approve_agent_execution_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_execution_env: None,
) -> None:
    submit = api_client.post(
        "/api/v1/llm/execution/steps",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.CASE_REVIEW.value,
            "step_summary": "Needs admin approval",
        },
    )
    assert submit.status_code == 200, submit.text
    step_id = submit.json()["step"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/execution/steps/{step_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_list_agent_execution_steps(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_execution_env: None,
) -> None:
    api_client.post(
        "/api/v1/llm/execution/steps",
        headers=manager_headers,
        json={
            "agent_kind": AgentObservabilityKind.DOCUMENT_TRIAGE.value,
            "step_summary": "Triage uploaded documents",
        },
    )
    response = api_client.get("/api/v1/llm/execution/steps", headers=manager_headers)
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
