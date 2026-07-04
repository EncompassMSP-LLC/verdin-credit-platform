"""Pydantic schemas for billing invoice collection scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.billing.collection_models import (
    BillingInvoiceCollectionRun,
    BillingInvoiceCollectionRunKind,
    BillingInvoiceCollectionRunStatus,
    BillingInvoiceCollectionTriggerSource,
)


class BillingInvoiceCollectionStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    invoicing_ready: bool
    blockers: list[str]


class BillingInvoiceCollectionRunRequest(BaseSchema):
    run_kind: BillingInvoiceCollectionRunKind = BillingInvoiceCollectionRunKind.INVOICE_PDF


class BillingInvoiceCollectionRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    run_kind: BillingInvoiceCollectionRunKind
    trigger_source: BillingInvoiceCollectionTriggerSource
    status: BillingInvoiceCollectionRunStatus
    invoices_pdf_generated: int
    payment_reminders_queued: int
    performed_by_user_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: BillingInvoiceCollectionRun) -> "BillingInvoiceCollectionRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            run_kind=run.run_kind,
            trigger_source=run.trigger_source,
            status=run.status,
            invoices_pdf_generated=run.invoices_pdf_generated,
            payment_reminders_queued=run.payment_reminders_queued,
            performed_by_user_id=run.performed_by_user_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class BillingInvoiceCollectionRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class BillingInvoiceCollectionRunResultResponse(BaseSchema):
    completed_at: datetime
    run: BillingInvoiceCollectionRunResponse
