"""Pydantic schemas for agent observability scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.agent_observability import AgentObservabilityStatus as AgentObservabilityGateStatus
from api.core.responses import BaseSchema
from api.modules.llm.agent_observability_models import (
    AgentObservabilityKind,
    AgentObservabilityRun,
    AgentObservabilityRunStatus,
    AgentObservabilityTriggerSource,
)


class AgentObservabilityStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    ai_enabled: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: AgentObservabilityGateStatus
    ) -> "AgentObservabilityStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            ai_enabled=status.ai_enabled,
            blockers=list(status.blockers),
        )


class AgentObservabilityRunRequest(BaseSchema):
    agent_kind: AgentObservabilityKind = AgentObservabilityKind.CASE_REVIEW
    case_id: uuid.UUID | None = None


class AgentObservabilityRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    agent_kind: AgentObservabilityKind
    trigger_source: AgentObservabilityTriggerSource
    status: AgentObservabilityRunStatus
    case_id: uuid.UUID | None
    steps_completed: int
    steps_failed: int
    timeline_event_id: uuid.UUID | None
    performed_by_user_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: AgentObservabilityRun) -> "AgentObservabilityRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            agent_kind=run.agent_kind,
            trigger_source=run.trigger_source,
            status=run.status,
            case_id=run.case_id,
            steps_completed=run.steps_completed,
            steps_failed=run.steps_failed,
            timeline_event_id=run.timeline_event_id,
            performed_by_user_id=run.performed_by_user_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class AgentObservabilityRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AgentObservabilityRunResultResponse(BaseSchema):
    completed_at: datetime
    run: AgentObservabilityRunResponse
