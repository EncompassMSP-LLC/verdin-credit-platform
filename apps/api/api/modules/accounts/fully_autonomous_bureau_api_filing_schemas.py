"""Pydantic schemas for admin-gated fully autonomous bureau API filing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.fully_autonomous_bureau_api_filing import (
    FullyAutonomousBureauApiFilingStatus as ApiFilingGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.accounts.fully_autonomous_bureau_api_filing_models import (
    FullyAutonomousBureauApiFilingRun,
    FullyAutonomousBureauApiFilingRunStatus,
)


class FullyAutonomousBureauApiFilingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    autonomous_bureau_filing_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: ApiFilingGateStatus
    ) -> "FullyAutonomousBureauApiFilingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            autonomous_bureau_filing_ready=status.autonomous_bureau_filing_ready,
            blockers=list(status.blockers),
        )


class FullyAutonomousBureauApiFilingSubmitRequest(BaseSchema):
    api_filing_summary: str = Field(min_length=1, max_length=2000)
    execution_reference_id: str | None = Field(default=None, max_length=128)


class FullyAutonomousBureauApiFilingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    autonomous_bureau_filing_run_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: FullyAutonomousBureauApiFilingRunStatus
    api_filing_summary: str
    execution_reference_id: str | None
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    executed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: FullyAutonomousBureauApiFilingRun
    ) -> "FullyAutonomousBureauApiFilingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            autonomous_bureau_filing_run_id=run.autonomous_bureau_filing_run_id,
            account_id=run.account_id,
            case_id=run.case_id,
            bureau_target=run.bureau_target,
            status=run.status,
            api_filing_summary=run.api_filing_summary,
            execution_reference_id=run.execution_reference_id,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            executed_at=run.executed_at,
            error_message=run.error_message,
        )


class FullyAutonomousBureauApiFilingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: FullyAutonomousBureauApiFilingRunResponse


class FullyAutonomousBureauApiFilingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
