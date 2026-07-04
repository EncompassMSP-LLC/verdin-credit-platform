"""Synchronous agent observability run processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.cases.repository import CaseRepository
from api.modules.llm.agent_observability_models import (
    AgentObservabilityKind,
    AgentObservabilityRun,
    AgentObservabilityRunStatus,
    AgentObservabilityTriggerSource,
)
from api.modules.llm.agent_observability_repository import AgentObservabilityRunRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AgentObservabilityRunSummary:
    run: AgentObservabilityRun
    completed_at: datetime


async def run_agent_observability_scaffold(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    agent_kind: AgentObservabilityKind,
    performed_by_user_id: uuid.UUID | None,
    case_id: uuid.UUID | None = None,
    run_repo: AgentObservabilityRunRepository | None = None,
    case_repo: CaseRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AgentObservabilityRunSummary:
    runs = run_repo or AgentObservabilityRunRepository(session)
    cases = case_repo or CaseRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    started_at = runs.utcnow()

    steps_completed = 0
    steps_failed = 0
    timeline_event_id: uuid.UUID | None = None
    resolved_case_id: uuid.UUID | None = None
    error_message: str | None = None

    if case_id is not None:
        case = await cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            steps_failed = 1
            error_message = "Case not found in organization"
        else:
            resolved_case_id = case.id
            steps_completed = 1
    else:
        steps_completed = 1

    run = await runs.create_run(
        organization_id=organization_id,
        agent_kind=agent_kind,
        trigger_source=AgentObservabilityTriggerSource.MANUAL,
        status=AgentObservabilityRunStatus.RUNNING,
        performed_by_user_id=performed_by_user_id,
        case_id=resolved_case_id,
        started_at=started_at,
    )

    if steps_failed > 0:
        run.status = AgentObservabilityRunStatus.FAILED
        run.steps_failed = steps_failed
        run.error_message = error_message
        run.completed_at = runs.utcnow()
        await session.flush()
        await session.refresh(run)
        return AgentObservabilityRunSummary(run=run, completed_at=run.completed_at)

    if resolved_case_id is not None:
        timeline_event = await timeline.append(
            TimelineEvent(
                organization_id=organization_id,
                case_id=resolved_case_id,
                event_type="agent_observability_run",
                event_category="ai",
                title=f"Agent run ({agent_kind.value})",
                description="Agent observability scaffold run recorded for staff review.",
                event_metadata={
                    "agent_kind": agent_kind.value,
                    "run_id": str(run.id),
                },
                performed_by=performed_by_user_id,
                source_module="agent_observability",
            )
        )
        timeline_event_id = timeline_event.id

    completed_at = runs.utcnow()
    run.status = AgentObservabilityRunStatus.COMPLETED
    run.steps_completed = steps_completed
    run.steps_failed = steps_failed
    run.timeline_event_id = timeline_event_id
    run.completed_at = completed_at
    await session.flush()
    await session.refresh(run)
    return AgentObservabilityRunSummary(run=run, completed_at=completed_at)
