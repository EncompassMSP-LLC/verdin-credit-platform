"""Pydantic schemas for admin-gated agent unsupervised loop scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.agent_unsupervised_loops import AgentUnsupervisedLoopStatus as LoopGateStatus
from api.core.responses import BaseSchema
from api.modules.llm.agent_unsupervised_loop_models import (
    AgentUnsupervisedLoopRun,
    AgentUnsupervisedLoopStatus,
)


class AgentUnsupervisedLoopStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    supervised_loops_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: LoopGateStatus) -> "AgentUnsupervisedLoopStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            supervised_loops_ready=status.supervised_loops_ready,
            blockers=list(status.blockers),
        )


class AgentUnsupervisedLoopSubmitRequest(BaseSchema):
    loop_summary: str = Field(min_length=1, max_length=2000)


class AgentUnsupervisedLoopRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    agent_supervised_loop_run_id: uuid.UUID
    case_id: uuid.UUID | None
    tool_kind: str
    status: AgentUnsupervisedLoopStatus
    loop_summary: str
    steps_completed: int
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: AgentUnsupervisedLoopRun) -> "AgentUnsupervisedLoopRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            agent_supervised_loop_run_id=run.agent_supervised_loop_run_id,
            case_id=run.case_id,
            tool_kind=run.tool_kind,
            status=run.status,
            loop_summary=run.loop_summary,
            steps_completed=run.steps_completed,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class AgentUnsupervisedLoopRunResultResponse(BaseSchema):
    completed_at: datetime
    run: AgentUnsupervisedLoopRunResponse


class AgentUnsupervisedLoopRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    case_id: uuid.UUID | None = None
