"""Human-gated agent external tool invocation scaffold integration tests."""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.modules.auth.models import Organization
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.llm.agent_tool_calling_models import AgentExternalToolKind


@pytest.fixture
def agent_tool_calling_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_AI", "true")
    monkeypatch.setenv("ENABLE_AGENT_OBSERVABILITY", "true")
    monkeypatch.setenv("ENABLE_AGENT_EXECUTION", "true")
    monkeypatch.setenv("ENABLE_AGENT_EXTERNAL_TOOL_CALLING", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def open_case(db_session: AsyncSession, test_org: Organization) -> Case:
    case = Case(
        organization_id=test_org.id,
        title="Agent tool calling case",
        client_name="Tool Client",
        status=CaseStatus.OPEN,
        stage=CaseStage.INTAKE,
        priority=CasePriority.MEDIUM,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


def test_agent_tool_calling_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/llm/tool-calling/status", headers=manager_headers)
    assert response.status_code == 404


def test_agent_tool_calling_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_tool_calling_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/tool-calling/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["agent_execution_ready"] is True
    assert payload["blockers"] == []


def test_submit_agent_tool_invocation_request(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_tool_calling_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.WEB_LOOKUP.value,
            "invocation_summary": "Lookup creditor contact details for staff review.",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["request"]["status"] == "pending_approval"
    assert payload["request"]["tool_kind"] == "web_lookup"


def test_submit_and_approve_agent_tool_invocation_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_tool_calling_env: None,
    open_case: Case,
) -> None:
    submit = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.DOCUMENT_FETCH.value,
            "invocation_summary": "Fetch supporting documents after human review.",
            "case_id": str(open_case.id),
        },
    )
    assert submit.status_code == 200, submit.text
    request_id = submit.json()["request"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/tool-calling/requests/{request_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["request"]
    assert approved["status"] == "invoked"
    assert approved["timeline_event_id"] is not None

    timeline = api_client.get(
        f"/api/v1/timeline?case_id={open_case.id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "agent_tool_invocation" for event in events)


def test_submit_agent_tool_invocation_unknown_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_tool_calling_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.CRM_UPDATE.value,
            "invocation_summary": "Missing case",
            "case_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 404
    assert "Case not found" in response.json()["detail"]


def test_approve_agent_tool_invocation_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_tool_calling_env: None,
) -> None:
    submit = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.WEB_LOOKUP.value,
            "invocation_summary": "Needs admin approval",
        },
    )
    assert submit.status_code == 200, submit.text
    request_id = submit.json()["request"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/tool-calling/requests/{request_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_list_agent_tool_invocation_requests(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_tool_calling_env: None,
) -> None:
    api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.DOCUMENT_FETCH.value,
            "invocation_summary": "List test tool invocation request",
        },
    )
    response = api_client.get("/api/v1/llm/tool-calling/requests", headers=manager_headers)
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
