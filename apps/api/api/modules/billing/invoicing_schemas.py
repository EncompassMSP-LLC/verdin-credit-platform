"""Pydantic schemas for billing invoicing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.billing.invoicing_models import (
    BillingInvoicingRun,
    BillingInvoicingRunKind,
    BillingInvoicingRunStatus,
    BillingInvoicingTriggerSource,
)


class BillingInvoicingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    billing_ready: bool
    blockers: list[str]


class BillingInvoicingRunRequest(BaseSchema):
    run_kind: BillingInvoicingRunKind = BillingInvoicingRunKind.INVOICE_CYCLE


class BillingInvoicingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    run_kind: BillingInvoicingRunKind
    trigger_source: BillingInvoicingTriggerSource
    status: BillingInvoicingRunStatus
    invoices_prepared: int
    dunning_reminders_queued: int
    performed_by_user_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: BillingInvoicingRun) -> "BillingInvoicingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            run_kind=run.run_kind,
            trigger_source=run.trigger_source,
            status=run.status,
            invoices_prepared=run.invoices_prepared,
            dunning_reminders_queued=run.dunning_reminders_queued,
            performed_by_user_id=run.performed_by_user_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class BillingInvoicingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class BillingInvoicingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: BillingInvoicingRunResponse
