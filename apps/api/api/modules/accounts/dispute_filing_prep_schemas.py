"""Pydantic schemas for compliance-gated dispute filing prep scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.dispute_filing_prep import DisputeFilingPrepStatus as PrepGateStatus
from api.core.responses import BaseSchema
from api.modules.accounts.dispute_filing_prep_models import (
    DisputeFilingPrepRun,
    DisputeFilingPrepStatus,
)
from api.modules.accounts.models import AccountBureau


class DisputeFilingPrepStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    agent_execution_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: PrepGateStatus) -> "DisputeFilingPrepStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            agent_execution_ready=status.agent_execution_ready,
            blockers=list(status.blockers),
        )


class DisputeFilingPrepRequest(BaseSchema):
    prep_summary: str = Field(min_length=1, max_length=2000)
    bureau_target: AccountBureau | None = None


class DisputeFilingPrepRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau_target: str
    status: DisputeFilingPrepStatus
    prep_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    timeline_event_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    prepared_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: DisputeFilingPrepRun) -> "DisputeFilingPrepRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            account_id=run.account_id,
            case_id=run.case_id,
            bureau_target=run.bureau_target,
            status=run.status,
            prep_summary=run.prep_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            timeline_event_id=run.timeline_event_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            prepared_at=run.prepared_at,
            error_message=run.error_message,
        )


class DisputeFilingPrepRunResultResponse(BaseSchema):
    completed_at: datetime
    run: DisputeFilingPrepRunResponse


class DisputeFilingPrepRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    account_id: uuid.UUID | None = None
