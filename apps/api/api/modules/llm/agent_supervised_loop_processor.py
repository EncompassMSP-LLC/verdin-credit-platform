"""Human-gated agent supervised loop processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_supervised_loop_models import (
    AgentSupervisedLoopRun,
    AgentSupervisedLoopStatus,
)
from api.modules.llm.agent_supervised_loop_repository import AgentSupervisedLoopRunRepository
from api.modules.llm.agent_tool_calling_models import AgentToolInvocationStatus
from api.modules.llm.agent_tool_calling_repository import AgentToolInvocationRequestRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AgentSupervisedLoopRunSummary:
    run: AgentSupervisedLoopRun
    completed_at: datetime


async def submit_agent_supervised_loop_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    tool_invocation_request_id: uuid.UUID,
    loop_summary: str,
    requested_by_user_id: uuid.UUID | None,
    loop_repo: AgentSupervisedLoopRunRepository | None = None,
    tool_repo: AgentToolInvocationRequestRepository | None = None,
) -> AgentSupervisedLoopRunSummary:
    loops = loop_repo or AgentSupervisedLoopRunRepository(session)
    tools = tool_repo or AgentToolInvocationRequestRepository(session)
    requested_at = loops.utcnow()

    tool_request = await tools.get_request_by_id(tool_invocation_request_id)
    if tool_request is None or tool_request.organization_id != organization_id:
        raise ValueError("Agent tool invocation request not found")
    if tool_request.status != AgentToolInvocationStatus.INVOKED:
        raise ValueError("Agent tool invocation request is not invoked")

    run = await loops.create_run(
        organization_id=organization_id,
        tool_invocation_request_id=tool_request.id,
        case_id=tool_request.case_id,
        tool_kind=tool_request.tool_kind.value,
        status=AgentSupervisedLoopStatus.PENDING_APPROVAL,
        loop_summary=loop_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return AgentSupervisedLoopRunSummary(run=run, completed_at=requested_at)


async def approve_agent_supervised_loop_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    loop_repo: AgentSupervisedLoopRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AgentSupervisedLoopRunSummary:
    loops = loop_repo or AgentSupervisedLoopRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = loops.utcnow()

    run = await loops.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Agent supervised loop run not found")
    if run.status != AgentSupervisedLoopStatus.PENDING_APPROVAL:
        raise ValueError("Agent supervised loop run is not pending approval")

    timeline_event_id: uuid.UUID | None = None
    if run.case_id is not None:
        timeline_event = await timeline.append(
            TimelineEvent(
                organization_id=organization_id,
                case_id=run.case_id,
                event_type="agent_supervised_loop",
                event_category="ai",
                title=f"Supervised agent loop step approved ({run.tool_kind})",
                description=run.loop_summary,
                event_metadata={
                    "tool_kind": run.tool_kind,
                    "run_id": str(run.id),
                    "tool_invocation_request_id": str(run.tool_invocation_request_id),
                    "approved_by_user_id": str(approved_by_user_id)
                    if approved_by_user_id
                    else None,
                },
                performed_by=approved_by_user_id,
                source_module="agent_supervised_loops",
            )
        )
        timeline_event_id = timeline_event.id

    completed_at = loops.utcnow()
    run.status = AgentSupervisedLoopStatus.COMPLETED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.completed_at = completed_at
    run.steps_completed = 1
    run.timeline_event_id = timeline_event_id
    await session.flush()
    await session.refresh(run)
    return AgentSupervisedLoopRunSummary(run=run, completed_at=completed_at)
