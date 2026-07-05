"""Pydantic schemas for human-gated agent external tool invocation scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.agent_external_tool_calling import (
    AgentExternalToolCallingStatus as ToolCallingGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.llm.agent_tool_calling_models import (
    AgentExternalToolKind,
    AgentToolInvocationRequest,
    AgentToolInvocationStatus,
)


class AgentExternalToolCallingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    agent_execution_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: ToolCallingGateStatus) -> "AgentExternalToolCallingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            agent_execution_ready=status.agent_execution_ready,
            blockers=list(status.blockers),
        )


class AgentToolInvocationSubmitRequest(BaseSchema):
    tool_kind: AgentExternalToolKind = AgentExternalToolKind.WEB_LOOKUP
    invocation_summary: str = Field(min_length=1, max_length=2000)
    case_id: uuid.UUID | None = None


class AgentToolInvocationRequestResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    tool_kind: AgentExternalToolKind
    status: AgentToolInvocationStatus
    case_id: uuid.UUID | None
    invocation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    invoked_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, request: AgentToolInvocationRequest
    ) -> "AgentToolInvocationRequestResponse":
        return cls(
            id=request.id,
            organization_id=request.organization_id,
            tool_kind=request.tool_kind,
            status=request.status,
            case_id=request.case_id,
            invocation_summary=request.invocation_summary,
            requested_by_user_id=request.requested_by_user_id,
            approved_by_user_id=request.approved_by_user_id,
            timeline_event_id=request.timeline_event_id,
            requested_at=request.requested_at,
            approved_at=request.approved_at,
            invoked_at=request.invoked_at,
            error_message=request.error_message,
        )


class AgentToolInvocationRequestResultResponse(BaseSchema):
    completed_at: datetime
    request: AgentToolInvocationRequestResponse


class AgentToolInvocationRequestListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    case_id: uuid.UUID | None = None
