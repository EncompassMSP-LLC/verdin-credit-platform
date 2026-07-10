"""Pydantic schemas for unsupervised autonomous filing loop scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.unsupervised_autonomous_filing_loops import (
    UnsupervisedAutonomousFilingLoopStatus as LoopGateStatus,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_models import (
    UnsupervisedAutonomousFilingLoopRun,
    UnsupervisedAutonomousFilingLoopRunStatus,
)


class UnsupervisedAutonomousFilingLoopStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    fully_autonomous_bureau_api_filing_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: LoopGateStatus
    ) -> "UnsupervisedAutonomousFilingLoopStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            fully_autonomous_bureau_api_filing_ready=status.fully_autonomous_bureau_api_filing_ready,
            blockers=list(status.blockers),
        )


class UnsupervisedAutonomousFilingLoopSubmitRequest(BaseSchema):
    loop_summary: str = Field(min_length=1, max_length=2000)
    loop_reference_id: str | None = Field(default=None, max_length=128)


class UnsupervisedAutonomousFilingLoopRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    fully_autonomous_bureau_api_filing_run_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: UnsupervisedAutonomousFilingLoopRunStatus
    loop_summary: str
    loop_reference_id: str | None
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: UnsupervisedAutonomousFilingLoopRun
    ) -> "UnsupervisedAutonomousFilingLoopRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            fully_autonomous_bureau_api_filing_run_id=run.fully_autonomous_bureau_api_filing_run_id,
            account_id=run.account_id,
            case_id=run.case_id,
            bureau_target=run.bureau_target,
            status=run.status,
            loop_summary=run.loop_summary,
            loop_reference_id=run.loop_reference_id,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            error_message=run.error_message,
        )


class UnsupervisedAutonomousFilingLoopRunResultResponse(BaseSchema):
    completed_at: datetime
    run: UnsupervisedAutonomousFilingLoopRunResponse


class UnsupervisedAutonomousFilingLoopRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
