"""Pydantic schemas for operator-gated bureau unsupervised re-filing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.bureau_unsupervised_refiling import (
    BureauUnsupervisedRefilingStatus as UnsupervisedGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.accounts.bureau_unsupervised_refiling_models import (
    BureauUnsupervisedRefilingRun,
    BureauUnsupervisedRefilingRunStatus,
)


class BureauUnsupervisedRefilingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    bureau_refiling_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: UnsupervisedGateStatus
    ) -> "BureauUnsupervisedRefilingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            bureau_refiling_ready=status.bureau_refiling_ready,
            blockers=list(status.blockers),
        )


class BureauUnsupervisedRefilingSubmitRequest(BaseSchema):
    refiling_summary: str = Field(min_length=1, max_length=2000)


class BureauUnsupervisedRefilingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    bureau_refiling_run_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: BureauUnsupervisedRefilingRunStatus
    refiling_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    unsupervised_refiled_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: BureauUnsupervisedRefilingRun
    ) -> "BureauUnsupervisedRefilingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            bureau_refiling_run_id=run.bureau_refiling_run_id,
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
            unsupervised_refiled_at=run.unsupervised_refiled_at,
            error_message=run.error_message,
        )


class BureauUnsupervisedRefilingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: BureauUnsupervisedRefilingRunResponse


class BureauUnsupervisedRefilingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
