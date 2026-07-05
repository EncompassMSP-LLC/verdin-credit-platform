"""Pydantic schemas for admin-gated dispute bureau submission scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.dispute_bureau_submission import DisputeBureauSubmissionStatus as SubmissionGateStatus
from api.core.responses import BaseSchema
from api.modules.accounts.dispute_bureau_submission_models import (
    DisputeBureauSubmissionRun,
    DisputeBureauSubmissionStatus,
)


class DisputeBureauSubmissionStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    filing_prep_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: SubmissionGateStatus) -> "DisputeBureauSubmissionStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            filing_prep_ready=status.filing_prep_ready,
            blockers=list(status.blockers),
        )


class DisputeBureauSubmissionRequest(BaseSchema):
    submission_summary: str = Field(min_length=1, max_length=2000)


class DisputeBureauSubmissionRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    filing_prep_run_id: uuid.UUID
    bureau_target: str
    status: DisputeBureauSubmissionStatus
    submission_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    submitted_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: DisputeBureauSubmissionRun) -> "DisputeBureauSubmissionRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            account_id=run.account_id,
            case_id=run.case_id,
            filing_prep_run_id=run.filing_prep_run_id,
            bureau_target=run.bureau_target,
            status=run.status,
            submission_summary=run.submission_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            submitted_at=run.submitted_at,
            error_message=run.error_message,
        )


class DisputeBureauSubmissionRunResultResponse(BaseSchema):
    completed_at: datetime
    run: DisputeBureauSubmissionRunResponse


class DisputeBureauSubmissionRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
