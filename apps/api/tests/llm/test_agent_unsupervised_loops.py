"""Admin-gated agent unsupervised loop scaffold integration tests."""

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
def agent_unsupervised_loops_env(
    monkeypatch: pytest.MonkeyPatch,
    agent_supervised_loops_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_AGENT_UNSUPERVISED_LOOPS", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def open_case(db_session: AsyncSession, test_org: Organization) -> Case:
    case = Case(
        organization_id=test_org.id,
        title="Agent unsupervised loop case",
        client_name="Unsupervised Loop Client",
        status=CaseStatus.OPEN,
        stage=CaseStage.INTAKE,
        priority=CasePriority.MEDIUM,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


def _complete_supervised_loop_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    *,
    case_id: str | None = None,
) -> str:
    payload: dict[str, str] = {
        "tool_kind": AgentExternalToolKind.DOCUMENT_FETCH.value,
        "invocation_summary": "Prepare unsupervised loop from completed supervised run.",
    }
    if case_id is not None:
        payload["case_id"] = case_id

    submit_tool = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json=payload,
    )
    assert submit_tool.status_code == 200, submit_tool.text
    request_id = submit_tool.json()["request"]["id"]

    approve_tool = api_client.post(
        f"/api/v1/llm/tool-calling/requests/{request_id}/approve",
        headers=admin_headers,
    )
    assert approve_tool.status_code == 200, approve_tool.text

    start_supervised = api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{request_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Supervised step before unsupervised loop."},
    )
    assert start_supervised.status_code == 200, start_supervised.text
    supervised_run_id = start_supervised.json()["run"]["id"]

    approve_supervised = api_client.post(
        f"/api/v1/llm/supervised-loops/runs/{supervised_run_id}/approve",
        headers=admin_headers,
    )
    assert approve_supervised.status_code == 200, approve_supervised.text
    assert approve_supervised.json()["run"]["status"] == "completed"
    return supervised_run_id


def test_agent_unsupervised_loops_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_supervised_loops_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/unsupervised-loops/status", headers=manager_headers)
    assert response.status_code == 404


def test_agent_unsupervised_loops_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_unsupervised_loops_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/unsupervised-loops/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["supervised_loops_ready"] is True
    assert payload["blockers"] == []


def test_submit_agent_unsupervised_loop_requires_completed_supervised_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_unsupervised_loops_env: None,
) -> None:
    submit_tool = api_client.post(
        "/api/v1/llm/tool-calling/requests",
        headers=manager_headers,
        json={
            "tool_kind": AgentExternalToolKind.WEB_LOOKUP.value,
            "invocation_summary": "Pending supervised loop approval.",
        },
    )
    assert submit_tool.status_code == 200, submit_tool.text
    request_id = submit_tool.json()["request"]["id"]

    approve_tool = api_client.post(
        f"/api/v1/llm/tool-calling/requests/{request_id}/approve",
        headers=admin_headers,
    )
    assert approve_tool.status_code == 200, approve_tool.text

    start_supervised = api_client.post(
        f"/api/v1/llm/supervised-loops/tool-requests/{request_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Not completed yet."},
    )
    assert start_supervised.status_code == 200, start_supervised.text
    supervised_run_id = start_supervised.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/llm/unsupervised-loops/supervised-runs/{supervised_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Cannot start unsupervised loop before supervised completion."},
    )
    assert response.status_code == 409
    assert "not completed" in response.json()["detail"]


def test_submit_and_approve_agent_unsupervised_loop_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_unsupervised_loops_env: None,
    open_case: Case,
) -> None:
    supervised_run_id = _complete_supervised_loop_run(
        api_client,
        manager_headers,
        admin_headers,
        case_id=str(open_case.id),
    )

    start = api_client.post(
        f"/api/v1/llm/unsupervised-loops/supervised-runs/{supervised_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Unsupervised multi-step loop after supervised completion."},
    )
    assert start.status_code == 200, start.text
    run = start.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["agent_supervised_loop_run_id"] == supervised_run_id
    assert run["case_id"] == str(open_case.id)

    approve = api_client.post(
        f"/api/v1/llm/unsupervised-loops/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "completed"
    assert approved["steps_completed"] == 3
    assert approved["timeline_event_id"] is not None

    timeline = api_client.get(
        f"/api/v1/timeline?case_id={open_case.id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "agent_unsupervised_loop" for event in events)


def test_approve_agent_unsupervised_loop_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_unsupervised_loops_env: None,
) -> None:
    supervised_run_id = _complete_supervised_loop_run(
        api_client,
        manager_headers,
        admin_headers,
    )

    start = api_client.post(
        f"/api/v1/llm/unsupervised-loops/supervised-runs/{supervised_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Needs admin approval for unsupervised loop."},
    )
    assert start.status_code == 200, start.text
    run_id = start.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/llm/unsupervised-loops/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_start_agent_unsupervised_loop_unknown_supervised_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    agent_unsupervised_loops_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/llm/unsupervised-loops/supervised-runs/{uuid.uuid4()}/start",
        headers=manager_headers,
        json={"loop_summary": "Missing supervised loop run"},
    )
    assert response.status_code == 404


def test_list_agent_unsupervised_loop_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_unsupervised_loops_env: None,
) -> None:
    supervised_run_id = _complete_supervised_loop_run(
        api_client,
        manager_headers,
        admin_headers,
    )
    api_client.post(
        f"/api/v1/llm/unsupervised-loops/supervised-runs/{supervised_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "List test unsupervised loop run"},
    )

    response = api_client.get("/api/v1/llm/unsupervised-loops/runs", headers=manager_headers)
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
