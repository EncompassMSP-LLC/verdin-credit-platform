"""Pydantic schemas for admin-gated Stripe tax calculation scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.stripe_tax_calculation import StripeTaxCalculationStatus as TaxGateStatus
from api.modules.billing.tax_calculation_models import (
    StripeTaxCalculationRun,
    StripeTaxCalculationRunStatus,
)


class StripeTaxCalculationStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    invoice_pdf_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: TaxGateStatus) -> "StripeTaxCalculationStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            invoice_pdf_ready=status.invoice_pdf_ready,
            blockers=list(status.blockers),
        )


class StripeTaxCalculationRequest(BaseSchema):
    calculation_summary: str = Field(min_length=1, max_length=2000)


class StripeTaxCalculationRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    invoice_pdf_run_id: uuid.UUID
    status: StripeTaxCalculationRunStatus
    calculation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    calculated_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: StripeTaxCalculationRun) -> "StripeTaxCalculationRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            invoice_pdf_run_id=run.invoice_pdf_run_id,
            status=run.status,
            calculation_summary=run.calculation_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            calculated_at=run.calculated_at,
            error_message=run.error_message,
        )


class StripeTaxCalculationRunResultResponse(BaseSchema):
    completed_at: datetime
    run: StripeTaxCalculationRunResponse


class StripeTaxCalculationRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
