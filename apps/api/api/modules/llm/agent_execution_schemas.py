"""Pydantic schemas for human-gated agent execution scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.agent_execution import AgentExecutionStatus as AgentExecutionGateStatus
from api.core.responses import BaseSchema
from api.modules.llm.agent_execution_models import (
    AgentExecutionStep,
    AgentExecutionStepStatus,
)
from api.modules.llm.agent_observability_models import AgentObservabilityKind


class AgentExecutionStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    observability_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: AgentExecutionGateStatus) -> "AgentExecutionStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            observability_ready=status.observability_ready,
            blockers=list(status.blockers),
        )


class AgentExecutionStepSubmitRequest(BaseSchema):
    agent_kind: AgentObservabilityKind = AgentObservabilityKind.CASE_REVIEW
    step_summary: str = Field(min_length=1, max_length=4000)
    case_id: uuid.UUID | None = None


class AgentExecutionStepResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    agent_kind: AgentObservabilityKind
    status: AgentExecutionStepStatus
    case_id: uuid.UUID | None
    step_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    executed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, step: AgentExecutionStep) -> "AgentExecutionStepResponse":
        return cls(
            id=step.id,
            organization_id=step.organization_id,
            agent_kind=step.agent_kind,
            status=step.status,
            case_id=step.case_id,
            step_summary=step.step_summary,
            requested_by_user_id=step.requested_by_user_id,
            approved_by_user_id=step.approved_by_user_id,
            timeline_event_id=step.timeline_event_id,
            requested_at=step.requested_at,
            approved_at=step.approved_at,
            executed_at=step.executed_at,
            error_message=step.error_message,
        )


class AgentExecutionStepListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AgentExecutionStepResultResponse(BaseSchema):
    completed_at: datetime
    step: AgentExecutionStepResponse
