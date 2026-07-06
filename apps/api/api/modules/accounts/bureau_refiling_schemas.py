"""Pydantic schemas for operator-gated bureau re-filing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.bureau_refiling import BureauRefilingStatus as RefilingGateStatus
from api.core.responses import BaseSchema
from api.modules.accounts.bureau_refiling_models import BureauRefilingRun, BureauRefilingRunStatus


class BureauRefilingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    autonomous_filing_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: RefilingGateStatus) -> "BureauRefilingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            autonomous_filing_ready=status.autonomous_filing_ready,
            blockers=list(status.blockers),
        )


class BureauRefilingSubmitRequest(BaseSchema):
    refiling_summary: str = Field(min_length=1, max_length=2000)


class BureauRefilingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    autonomous_bureau_filing_run_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: BureauRefilingRunStatus
    refiling_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    refiled_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: BureauRefilingRun) -> "BureauRefilingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            autonomous_bureau_filing_run_id=run.autonomous_bureau_filing_run_id,
            account_id=run.account_id,
            case_id=run.case_id,
            bureau_target=run.bureau_target,
            status=run.status,
            refiling_summary=run.refiling_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            refiled_at=run.refiled_at,
            error_message=run.error_message,
        )


class BureauRefilingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: BureauRefilingRunResponse


class BureauRefilingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
