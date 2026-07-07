"""Pydantic schemas for operator-gated bureau live API scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.bureau_live_api import BureauLiveApiStatus as LiveApiGateStatus
from api.core.responses import BaseSchema
from api.modules.accounts.bureau_live_api_models import BureauLiveApiRun, BureauLiveApiRunStatus


class BureauLiveApiStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    bureau_submission_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: LiveApiGateStatus) -> "BureauLiveApiStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            bureau_submission_ready=status.bureau_submission_ready,
            blockers=list(status.blockers),
        )


class BureauLiveApiInvokeRequest(BaseSchema):
    invocation_summary: str = Field(min_length=1, max_length=2000)


class BureauLiveApiRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    bureau_submission_run_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: BureauLiveApiRunStatus
    invocation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    invocation_reference_id: str | None
    invocation_channel: str | None
    requested_at: datetime | None
    approved_at: datetime | None
    invoked_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: BureauLiveApiRun) -> "BureauLiveApiRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            bureau_submission_run_id=run.bureau_submission_run_id,
            account_id=run.account_id,
            case_id=run.case_id,
            bureau_target=run.bureau_target,
            status=run.status,
            invocation_summary=run.invocation_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            invocation_reference_id=run.invocation_reference_id,
            invocation_channel=run.invocation_channel,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            invoked_at=run.invoked_at,
            error_message=run.error_message,
        )


class BureauLiveApiRunResultResponse(BaseSchema):
    completed_at: datetime
    run: BureauLiveApiRunResponse


class BureauLiveApiRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
