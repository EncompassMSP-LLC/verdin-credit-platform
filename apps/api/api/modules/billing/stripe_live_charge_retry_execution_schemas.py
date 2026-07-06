"""Pydantic schemas for admin-gated Stripe live charge retry execution scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.stripe_live_charge_retry_execution import (
    StripeLiveChargeRetryExecutionStatus as ExecutionGateStatus,
)
from api.modules.billing.stripe_live_charge_retry_execution_models import (
    StripeLiveChargeRetryExecutionRun,
    StripeLiveChargeRetryExecutionRunStatus,
)


class StripeLiveChargeRetryExecutionStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    charge_retry_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: ExecutionGateStatus
    ) -> "StripeLiveChargeRetryExecutionStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            charge_retry_ready=status.charge_retry_ready,
            blockers=list(status.blockers),
        )


class StripeLiveChargeRetryExecutionSubmitRequest(BaseSchema):
    execution_summary: str = Field(min_length=1, max_length=2000)


class StripeLiveChargeRetryExecutionRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    stripe_charge_retry_run_id: uuid.UUID
    status: StripeLiveChargeRetryExecutionRunStatus
    execution_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    executed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: StripeLiveChargeRetryExecutionRun
    ) -> "StripeLiveChargeRetryExecutionRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            stripe_charge_retry_run_id=run.stripe_charge_retry_run_id,
            status=run.status,
            execution_summary=run.execution_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            executed_at=run.executed_at,
            error_message=run.error_message,
        )


class StripeLiveChargeRetryExecutionRunResultResponse(BaseSchema):
    completed_at: datetime
    run: StripeLiveChargeRetryExecutionRunResponse


class StripeLiveChargeRetryExecutionRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
