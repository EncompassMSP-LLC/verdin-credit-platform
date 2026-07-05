"""Pydantic schemas for admin-gated autonomous bureau filing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.autonomous_bureau_filing import AutonomousBureauFilingStatus as FilingGateStatus
from api.core.responses import BaseSchema
from api.modules.accounts.autonomous_bureau_filing_models import (
    AutonomousBureauFilingRun,
    AutonomousBureauFilingRunStatus,
)


class AutonomousBureauFilingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    bureau_live_api_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: FilingGateStatus) -> "AutonomousBureauFilingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            bureau_live_api_ready=status.bureau_live_api_ready,
            blockers=list(status.blockers),
        )


class AutonomousBureauFilingSubmitRequest(BaseSchema):
    filing_summary: str = Field(min_length=1, max_length=2000)


class AutonomousBureauFilingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    bureau_live_api_run_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: AutonomousBureauFilingRunStatus
    filing_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    filed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: AutonomousBureauFilingRun) -> "AutonomousBureauFilingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            bureau_live_api_run_id=run.bureau_live_api_run_id,
            account_id=run.account_id,
            case_id=run.case_id,
            bureau_target=run.bureau_target,
            status=run.status,
            filing_summary=run.filing_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            filed_at=run.filed_at,
            error_message=run.error_message,
        )


class AutonomousBureauFilingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: AutonomousBureauFilingRunResponse


class AutonomousBureauFilingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
