"""Pydantic schemas for admin-gated Stripe live Tax API scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.stripe_live_tax_api import StripeLiveTaxApiStatus as LiveTaxGateStatus
from api.modules.billing.stripe_live_tax_api_models import (
    StripeLiveTaxApiRun,
    StripeLiveTaxApiRunStatus,
)


class StripeLiveTaxApiStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    tax_calculation_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: LiveTaxGateStatus) -> "StripeLiveTaxApiStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            tax_calculation_ready=status.tax_calculation_ready,
            blockers=list(status.blockers),
        )


class StripeLiveTaxApiInvokeRequest(BaseSchema):
    invocation_summary: str = Field(min_length=1, max_length=2000)


class StripeLiveTaxApiRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    stripe_tax_calculation_run_id: uuid.UUID
    status: StripeLiveTaxApiRunStatus
    invocation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    invoked_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: StripeLiveTaxApiRun) -> "StripeLiveTaxApiRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            stripe_tax_calculation_run_id=run.stripe_tax_calculation_run_id,
            status=run.status,
            invocation_summary=run.invocation_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            invoked_at=run.invoked_at,
            error_message=run.error_message,
        )


class StripeLiveTaxApiRunResultResponse(BaseSchema):
    completed_at: datetime
    run: StripeLiveTaxApiRunResponse


class StripeLiveTaxApiRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
