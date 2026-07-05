"""Pydantic schemas for admin-gated agent arbitrary execution scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.agent_arbitrary_execution import AgentArbitraryExecutionStatus as ExecutionGateStatus
from api.core.responses import BaseSchema
from api.modules.llm.agent_arbitrary_execution_models import (
    AgentArbitraryExecutionRun,
    AgentArbitraryExecutionRunStatus,
)


class AgentArbitraryExecutionStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    unsupervised_loops_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: ExecutionGateStatus) -> "AgentArbitraryExecutionStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            unsupervised_loops_ready=status.unsupervised_loops_ready,
            blockers=list(status.blockers),
        )


class AgentArbitraryExecutionSubmitRequest(BaseSchema):
    execution_summary: str = Field(min_length=1, max_length=2000)


class AgentArbitraryExecutionRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    agent_unsupervised_loop_run_id: uuid.UUID
    case_id: uuid.UUID | None
    tool_kind: str
    status: AgentArbitraryExecutionRunStatus
    execution_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    executed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: AgentArbitraryExecutionRun) -> "AgentArbitraryExecutionRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            agent_unsupervised_loop_run_id=run.agent_unsupervised_loop_run_id,
            case_id=run.case_id,
            tool_kind=run.tool_kind,
            status=run.status,
            execution_summary=run.execution_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            executed_at=run.executed_at,
            error_message=run.error_message,
        )


class AgentArbitraryExecutionRunResultResponse(BaseSchema):
    completed_at: datetime
    run: AgentArbitraryExecutionRunResponse


class AgentArbitraryExecutionRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    case_id: uuid.UUID | None = None
