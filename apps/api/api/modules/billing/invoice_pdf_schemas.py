"""Pydantic schemas for admin-gated Stripe invoice PDF generation scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.stripe_invoice_pdf import StripeInvoicePdfStatus as PdfGateStatus
from api.modules.billing.invoice_pdf_models import StripeInvoicePdfRun, StripeInvoicePdfRunStatus


class StripeInvoicePdfStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    collection_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: PdfGateStatus) -> "StripeInvoicePdfStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            collection_ready=status.collection_ready,
            blockers=list(status.blockers),
        )


class StripeInvoicePdfRequest(BaseSchema):
    generation_summary: str = Field(min_length=1, max_length=2000)


class StripeInvoicePdfRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    collection_run_id: uuid.UUID
    status: StripeInvoicePdfRunStatus
    generation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    generated_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: StripeInvoicePdfRun) -> "StripeInvoicePdfRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            collection_run_id=run.collection_run_id,
            status=run.status,
            generation_summary=run.generation_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            generated_at=run.generated_at,
            error_message=run.error_message,
        )


class StripeInvoicePdfRunResultResponse(BaseSchema):
    completed_at: datetime
    run: StripeInvoicePdfRunResponse


class StripeInvoicePdfRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
