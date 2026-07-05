"""Admin-gated agent unsupervised loop processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_supervised_loop_models import AgentSupervisedLoopStatus
from api.modules.llm.agent_supervised_loop_repository import AgentSupervisedLoopRunRepository
from api.modules.llm.agent_unsupervised_loop_models import (
    AgentUnsupervisedLoopRun,
    AgentUnsupervisedLoopStatus,
)
from api.modules.llm.agent_unsupervised_loop_repository import AgentUnsupervisedLoopRunRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AgentUnsupervisedLoopRunSummary:
    run: AgentUnsupervisedLoopRun
    completed_at: datetime


async def submit_agent_unsupervised_loop_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    agent_supervised_loop_run_id: uuid.UUID,
    loop_summary: str,
    requested_by_user_id: uuid.UUID | None,
    loop_repo: AgentUnsupervisedLoopRunRepository | None = None,
    supervised_repo: AgentSupervisedLoopRunRepository | None = None,
) -> AgentUnsupervisedLoopRunSummary:
    loops = loop_repo or AgentUnsupervisedLoopRunRepository(session)
    supervised = supervised_repo or AgentSupervisedLoopRunRepository(session)
    requested_at = loops.utcnow()

    supervised_run = await supervised.get_run_by_id(agent_supervised_loop_run_id)
    if supervised_run is None or supervised_run.organization_id != organization_id:
        raise ValueError("Agent supervised loop run not found")
    if supervised_run.status != AgentSupervisedLoopStatus.COMPLETED:
        raise ValueError("Agent supervised loop run is not completed")

    run = await loops.create_run(
        organization_id=organization_id,
        agent_supervised_loop_run_id=supervised_run.id,
        case_id=supervised_run.case_id,
        tool_kind=supervised_run.tool_kind,
        status=AgentUnsupervisedLoopStatus.PENDING_APPROVAL,
        loop_summary=loop_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return AgentUnsupervisedLoopRunSummary(run=run, completed_at=requested_at)


async def approve_agent_unsupervised_loop_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    loop_repo: AgentUnsupervisedLoopRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AgentUnsupervisedLoopRunSummary:
    loops = loop_repo or AgentUnsupervisedLoopRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = loops.utcnow()

    run = await loops.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Agent unsupervised loop run not found")
    if run.status != AgentUnsupervisedLoopStatus.PENDING_APPROVAL:
        raise ValueError("Agent unsupervised loop run is not pending approval")

    timeline_event_id: uuid.UUID | None = None
    if run.case_id is not None:
        timeline_event = await timeline.append(
            TimelineEvent(
                organization_id=organization_id,
                case_id=run.case_id,
                event_type="agent_unsupervised_loop",
                event_category="ai",
                title=f"Unsupervised agent loop approved ({run.tool_kind})",
                description=run.loop_summary,
                event_metadata={
                    "tool_kind": run.tool_kind,
                    "run_id": str(run.id),
                    "agent_supervised_loop_run_id": str(run.agent_supervised_loop_run_id),
                    "approved_by_user_id": str(approved_by_user_id)
                    if approved_by_user_id
                    else None,
                },
                performed_by=approved_by_user_id,
                source_module="agent_unsupervised_loops",
            )
        )
        timeline_event_id = timeline_event.id

    completed_at = loops.utcnow()
    run.status = AgentUnsupervisedLoopStatus.COMPLETED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.completed_at = completed_at
    run.steps_completed = 3
    run.timeline_event_id = timeline_event_id
    await session.flush()
    await session.refresh(run)
    return AgentUnsupervisedLoopRunSummary(run=run, completed_at=completed_at)
