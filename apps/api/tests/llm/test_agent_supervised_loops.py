"""Human-gated agent supervised loop scaffold integration tests."""

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
def agent_supervised_loops_env(
    monkeypatch: pytest.MonkeyPatch,
    agent_tool_calling_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_AGENT_SUPERVISED_LOOPS", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def open_case(db_session: AsyncSession, test_org: Organization) -> Case:
    case = Case(
        organization_id=test_org.id,
        title="Agent supervised loop case",
        client_name="Loop Client",
        status=CaseStatus.OPEN,
        stage=CaseStage.INTAKE,
        priority=CasePriority.MEDIUM,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


def _submit_and_approve_tool_request(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    *,
    case_id: str | None = None,
) -> str:
    payload: dict[str, str] = {
        "tool_kind": AgentExternalToolKind.DOCUMENT_FETCH.value,
        "invocation_summary": "Prepare supervised loop from invoked tool request.",
    }
    if case_id is not None:
        payload["case_id"] = case_id

    submit = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json=payload,
    )
    assert submit.status_code == 200, submit.text
    request_id = submit.json()["request"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/tool-calling/requests/{request_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["request"]["status"] == "invoked"
    return request_id


def test_agent_supervised_loops_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_tool_calling_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/supervised-loops/status", headers=manager_headers)
    assert response.status_code == 404


def test_agent_supervised_loops_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_supervised_loops_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/supervised-loops/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["tool_calling_ready"] is True
    assert payload["blockers"] == []


def test_submit_agent_supervised_loop_requires_invoked_tool_request(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_supervised_loops_env: None,
) -> None:
    submit_tool = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.WEB_LOOKUP.value,
            "invocation_summary": "Pending approval — cannot start supervised loop yet.",
        },
    )
    assert submit_tool.status_code == 200, submit_tool.text
    request_id = submit_tool.json()["request"]["id"]

    response = api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{request_id}/start",
        headers=manager_headers,
        json={"loop_summary": "First supervised loop step after tool invocation."},
    )
    assert response.status_code == 409
    assert "not invoked" in response.json()["detail"]


def test_submit_and_approve_agent_supervised_loop_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_supervised_loops_env: None,
    open_case: Case,
) -> None:
    request_id = _submit_and_approve_tool_request(
        api_client,
        manager_headers,
        admin_headers,
        case_id=str(open_case.id),
    )

    start = api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{request_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Supervised loop step after document fetch invocation."},
    )
    assert start.status_code == 200, start.text
    run = start.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["tool_invocation_request_id"] == request_id
    assert run["case_id"] == str(open_case.id)

    approve = api_client.post(
        f"/api/v1/llm/supervised-loops/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "completed"
    assert approved["steps_completed"] == 1
    assert approved["timeline_event_id"] is not None

    timeline = api_client.get(
        f"/api/v1/timeline?case_id={open_case.id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "agent_supervised_loop" for event in events)


def test_approve_agent_supervised_loop_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_supervised_loops_env: None,
) -> None:
    request_id = _submit_and_approve_tool_request(
        api_client,
        manager_headers,
        admin_headers,
    )

    start = api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{request_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Needs admin approval for supervised loop step."},
    )
    assert start.status_code == 200, start.text
    run_id = start.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/supervised-loops/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_start_agent_supervised_loop_unknown_tool_request(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_supervised_loops_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{uuid.uuid4()}/start",
        headers=manager_headers,
        json={"loop_summary": "Missing tool invocation request"},
    )
    assert response.status_code == 404


def test_list_agent_supervised_loop_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_supervised_loops_env: None,
) -> None:
    request_id = _submit_and_approve_tool_request(
        api_client,
        manager_headers,
        admin_headers,
    )
    api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{request_id}/start",
        headers=manager_headers,
        json={"loop_summary": "List test supervised loop run"},
    )

    response = api_client.get("/api/v1/llm/supervised-loops/runs", headers=manager_headers)
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
