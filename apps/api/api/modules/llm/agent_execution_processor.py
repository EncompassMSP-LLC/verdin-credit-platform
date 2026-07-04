"""Human-gated agent execution processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.cases.repository import CaseRepository
from api.modules.llm.agent_execution_models import AgentExecutionStep, AgentExecutionStepStatus
from api.modules.llm.agent_execution_repository import AgentExecutionStepRepository
from api.modules.llm.agent_observability_models import AgentObservabilityKind
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AgentExecutionStepSummary:
    step: AgentExecutionStep
    completed_at: datetime


async def submit_agent_execution_step(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    agent_kind: AgentObservabilityKind,
    step_summary: str,
    requested_by_user_id: uuid.UUID | None,
    case_id: uuid.UUID | None = None,
    step_repo: AgentExecutionStepRepository | None = None,
    case_repo: CaseRepository | None = None,
) -> AgentExecutionStepSummary:
    steps = step_repo or AgentExecutionStepRepository(session)
    cases = case_repo or CaseRepository(session)
    requested_at = steps.utcnow()

    resolved_case_id: uuid.UUID | None = None
    if case_id is not None:
        case = await cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            step = await steps.create_step(
                organization_id=organization_id,
                agent_kind=agent_kind,
                status=AgentExecutionStepStatus.FAILED,
                step_summary=step_summary,
                requested_by_user_id=requested_by_user_id,
                case_id=None,
                requested_at=requested_at,
                error_message="Case not found in organization",
            )
            return AgentExecutionStepSummary(step=step, completed_at=requested_at)
        resolved_case_id = case.id

    step = await steps.create_step(
        organization_id=organization_id,
        agent_kind=agent_kind,
        status=AgentExecutionStepStatus.PENDING_APPROVAL,
        step_summary=step_summary,
        requested_by_user_id=requested_by_user_id,
        case_id=resolved_case_id,
        requested_at=requested_at,
    )
    return AgentExecutionStepSummary(step=step, completed_at=requested_at)


async def approve_agent_execution_step(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    step_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    step_repo: AgentExecutionStepRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AgentExecutionStepSummary:
    steps = step_repo or AgentExecutionStepRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = steps.utcnow()

    step = await steps.get_step_by_id(step_id)
    if step is None or step.organization_id != organization_id:
        raise ValueError("Agent execution step not found")
    if step.status != AgentExecutionStepStatus.PENDING_APPROVAL:
        raise ValueError("Agent execution step is not pending approval")

    timeline_event_id: uuid.UUID | None = None
    if step.case_id is not None:
        timeline_event = await timeline.append(
            TimelineEvent(
                organization_id=organization_id,
                case_id=step.case_id,
                event_type="agent_execution_step",
                event_category="ai",
                title=f"Agent step approved ({step.agent_kind.value})",
                description=step.step_summary,
                event_metadata={
                    "agent_kind": step.agent_kind.value,
                    "step_id": str(step.id),
                    "approved_by_user_id": str(approved_by_user_id)
                    if approved_by_user_id
                    else None,
                },
                performed_by=approved_by_user_id,
                source_module="agent_execution",
            )
        )
        timeline_event_id = timeline_event.id

    executed_at = steps.utcnow()
    step.status = AgentExecutionStepStatus.EXECUTED
    step.approved_by_user_id = approved_by_user_id
    step.approved_at = approved_at
    step.executed_at = executed_at
    step.timeline_event_id = timeline_event_id
    await session.flush()
    await session.refresh(step)
    return AgentExecutionStepSummary(step=step, completed_at=executed_at)
