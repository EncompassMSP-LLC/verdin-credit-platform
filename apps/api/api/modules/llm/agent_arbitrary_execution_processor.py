"""Admin-gated agent arbitrary execution processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_arbitrary_execution_models import (
    AgentArbitraryExecutionRun,
    AgentArbitraryExecutionRunStatus,
)
from api.modules.llm.agent_arbitrary_execution_repository import (
    AgentArbitraryExecutionRunRepository,
)
from api.modules.llm.agent_unsupervised_loop_models import AgentUnsupervisedLoopStatus
from api.modules.llm.agent_unsupervised_loop_repository import AgentUnsupervisedLoopRunRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AgentArbitraryExecutionRunSummary:
    run: AgentArbitraryExecutionRun
    completed_at: datetime


async def submit_agent_arbitrary_execution_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    agent_unsupervised_loop_run_id: uuid.UUID,
    execution_summary: str,
    requested_by_user_id: uuid.UUID | None,
    execution_repo: AgentArbitraryExecutionRunRepository | None = None,
    unsupervised_repo: AgentUnsupervisedLoopRunRepository | None = None,
) -> AgentArbitraryExecutionRunSummary:
    executions = execution_repo or AgentArbitraryExecutionRunRepository(session)
    unsupervised = unsupervised_repo or AgentUnsupervisedLoopRunRepository(session)
    requested_at = executions.utcnow()

    unsupervised_run = await unsupervised.get_run_by_id(agent_unsupervised_loop_run_id)
    if unsupervised_run is None or unsupervised_run.organization_id != organization_id:
        raise ValueError("Agent unsupervised loop run not found")
    if unsupervised_run.status != AgentUnsupervisedLoopStatus.COMPLETED:
        raise ValueError("Agent unsupervised loop run is not completed")

    run = await executions.create_run(
        organization_id=organization_id,
        agent_unsupervised_loop_run_id=unsupervised_run.id,
        case_id=unsupervised_run.case_id,
        tool_kind=unsupervised_run.tool_kind,
        status=AgentArbitraryExecutionRunStatus.PENDING_APPROVAL,
        execution_summary=execution_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return AgentArbitraryExecutionRunSummary(run=run, completed_at=requested_at)


async def approve_agent_arbitrary_execution_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    execution_repo: AgentArbitraryExecutionRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AgentArbitraryExecutionRunSummary:
    executions = execution_repo or AgentArbitraryExecutionRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = executions.utcnow()

    run = await executions.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Agent arbitrary execution run not found")
    if run.status != AgentArbitraryExecutionRunStatus.PENDING_APPROVAL:
        raise ValueError("Agent arbitrary execution run is not pending approval")

    timeline_event_id: uuid.UUID | None = None
    if run.case_id is not None:
        timeline_event = await timeline.append(
            TimelineEvent(
                organization_id=organization_id,
                case_id=run.case_id,
                event_type="agent_arbitrary_execution",
                event_category="ai",
                title=f"Arbitrary agent execution approved ({run.tool_kind})",
                description=run.execution_summary,
                event_metadata={
                    "tool_kind": run.tool_kind,
                    "run_id": str(run.id),
                    "agent_unsupervised_loop_run_id": str(run.agent_unsupervised_loop_run_id),
                    "approved_by_user_id": str(approved_by_user_id)
                    if approved_by_user_id
                    else None,
                },
                performed_by=approved_by_user_id,
                source_module="agent_arbitrary_execution",
            )
        )
        timeline_event_id = timeline_event.id

    executed_at = executions.utcnow()
    run.status = AgentArbitraryExecutionRunStatus.EXECUTED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.executed_at = executed_at
    run.timeline_event_id = timeline_event_id
    await session.flush()
    await session.refresh(run)
    return AgentArbitraryExecutionRunSummary(run=run, completed_at=executed_at)
