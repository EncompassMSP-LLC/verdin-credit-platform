"""Pydantic schemas for admin-gated Stripe charge retry scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.stripe_charge_retry import StripeChargeRetryStatus as RetryGateStatus
from api.modules.billing.stripe_charge_retry_models import (
    StripeChargeRetryRun,
    StripeChargeRetryRunStatus,
)


class StripeChargeRetryStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    live_tax_api_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: RetryGateStatus) -> "StripeChargeRetryStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            live_tax_api_ready=status.live_tax_api_ready,
            blockers=list(status.blockers),
        )


class StripeChargeRetrySubmitRequest(BaseSchema):
    retry_summary: str = Field(min_length=1, max_length=2000)


class StripeChargeRetryRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    stripe_live_tax_api_run_id: uuid.UUID
    status: StripeChargeRetryRunStatus
    retry_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    retried_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: StripeChargeRetryRun) -> "StripeChargeRetryRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            stripe_live_tax_api_run_id=run.stripe_live_tax_api_run_id,
            status=run.status,
            retry_summary=run.retry_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            retried_at=run.retried_at,
            error_message=run.error_message,
        )


class StripeChargeRetryRunResultResponse(BaseSchema):
    completed_at: datetime
    run: StripeChargeRetryRunResponse


class StripeChargeRetryRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
