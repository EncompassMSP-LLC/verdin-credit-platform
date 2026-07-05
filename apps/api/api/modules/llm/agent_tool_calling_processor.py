"""Human-gated agent external tool invocation processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.cases.repository import CaseRepository
from api.modules.llm.agent_tool_calling_models import (
    AgentExternalToolKind,
    AgentToolInvocationRequest,
    AgentToolInvocationStatus,
)
from api.modules.llm.agent_tool_calling_repository import AgentToolInvocationRequestRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AgentToolInvocationRequestSummary:
    request: AgentToolInvocationRequest
    completed_at: datetime


async def submit_agent_tool_invocation_request(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    tool_kind: AgentExternalToolKind,
    invocation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    case_id: uuid.UUID | None = None,
    request_repo: AgentToolInvocationRequestRepository | None = None,
    case_repo: CaseRepository | None = None,
) -> AgentToolInvocationRequestSummary:
    requests = request_repo or AgentToolInvocationRequestRepository(session)
    cases = case_repo or CaseRepository(session)
    requested_at = requests.utcnow()

    resolved_case_id: uuid.UUID | None = None
    if case_id is not None:
        case = await cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            request = await requests.create_request(
                organization_id=organization_id,
                tool_kind=tool_kind,
                status=AgentToolInvocationStatus.FAILED,
                invocation_summary=invocation_summary,
                requested_by_user_id=requested_by_user_id,
                case_id=None,
                requested_at=requested_at,
                error_message="Case not found in organization",
            )
            return AgentToolInvocationRequestSummary(request=request, completed_at=requested_at)
        resolved_case_id = case.id

    request = await requests.create_request(
        organization_id=organization_id,
        tool_kind=tool_kind,
        status=AgentToolInvocationStatus.PENDING_APPROVAL,
        invocation_summary=invocation_summary,
        requested_by_user_id=requested_by_user_id,
        case_id=resolved_case_id,
        requested_at=requested_at,
    )
    return AgentToolInvocationRequestSummary(request=request, completed_at=requested_at)


async def approve_agent_tool_invocation_request(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    request_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    request_repo: AgentToolInvocationRequestRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AgentToolInvocationRequestSummary:
    requests = request_repo or AgentToolInvocationRequestRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = requests.utcnow()

    request = await requests.get_request_by_id(request_id)
    if request is None or request.organization_id != organization_id:
        raise ValueError("Agent tool invocation request not found")
    if request.status != AgentToolInvocationStatus.PENDING_APPROVAL:
        raise ValueError("Agent tool invocation request is not pending approval")

    timeline_event_id: uuid.UUID | None = None
    if request.case_id is not None:
        timeline_event = await timeline.append(
            TimelineEvent(
                organization_id=organization_id,
                case_id=request.case_id,
                event_type="agent_tool_invocation",
                event_category="ai",
                title=f"External tool invocation approved ({request.tool_kind.value})",
                description=request.invocation_summary,
                event_metadata={
                    "tool_kind": request.tool_kind.value,
                    "request_id": str(request.id),
                    "approved_by_user_id": str(approved_by_user_id)
                    if approved_by_user_id
                    else None,
                },
                performed_by=approved_by_user_id,
                source_module="agent_tool_calling",
            )
        )
        timeline_event_id = timeline_event.id

    invoked_at = requests.utcnow()
    request.status = AgentToolInvocationStatus.INVOKED
    request.approved_by_user_id = approved_by_user_id
    request.approved_at = approved_at
    request.invoked_at = invoked_at
    request.timeline_event_id = timeline_event_id
    await session.flush()
    await session.refresh(request)
    return AgentToolInvocationRequestSummary(request=request, completed_at=invoked_at)
