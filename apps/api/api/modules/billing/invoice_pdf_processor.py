"""Admin-gated Stripe invoice PDF generation processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.collection_models import (
    BillingInvoiceCollectionRunKind,
    BillingInvoiceCollectionRunStatus,
)
from api.modules.billing.collection_repository import BillingInvoiceCollectionRunRepository
from api.modules.billing.invoice_pdf_models import StripeInvoicePdfRun, StripeInvoicePdfRunStatus
from api.modules.billing.invoice_pdf_repository import StripeInvoicePdfRunRepository


@dataclass(frozen=True)
class StripeInvoicePdfRunSummary:
    run: StripeInvoicePdfRun
    completed_at: datetime


async def submit_stripe_invoice_pdf_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    collection_run_id: uuid.UUID,
    generation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    pdf_repo: StripeInvoicePdfRunRepository | None = None,
    collection_repo: BillingInvoiceCollectionRunRepository | None = None,
) -> StripeInvoicePdfRunSummary:
    pdf_runs = pdf_repo or StripeInvoicePdfRunRepository(session)
    collections = collection_repo or BillingInvoiceCollectionRunRepository(session)
    requested_at = pdf_runs.utcnow()

    collection_run = await collections.get_run_by_id(collection_run_id)
    if collection_run is None or collection_run.organization_id != organization_id:
        raise ValueError("Billing invoice collection run not found")
    if collection_run.status != BillingInvoiceCollectionRunStatus.COMPLETED:
        raise ValueError("Billing invoice collection run is not completed")
    if collection_run.run_kind != BillingInvoiceCollectionRunKind.INVOICE_PDF:
        raise ValueError("Billing invoice collection run is not an invoice PDF run")
    if collection_run.invoices_pdf_generated <= 0:
        raise ValueError("Billing invoice collection run did not generate invoice PDFs")

    run = await pdf_runs.create_run(
        organization_id=organization_id,
        collection_run_id=collection_run.id,
        status=StripeInvoicePdfRunStatus.PENDING_APPROVAL,
        generation_summary=generation_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return StripeInvoicePdfRunSummary(run=run, completed_at=requested_at)


async def approve_stripe_invoice_pdf_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    pdf_repo: StripeInvoicePdfRunRepository | None = None,
) -> StripeInvoicePdfRunSummary:
    pdf_runs = pdf_repo or StripeInvoicePdfRunRepository(session)
    approved_at = pdf_runs.utcnow()

    run = await pdf_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Stripe invoice PDF run not found")
    if run.status != StripeInvoicePdfRunStatus.PENDING_APPROVAL:
        raise ValueError("Stripe invoice PDF run is not pending approval")

    generated_at = pdf_runs.utcnow()
    run.status = StripeInvoicePdfRunStatus.GENERATED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.generated_at = generated_at
    await session.flush()
    await session.refresh(run)
    return StripeInvoicePdfRunSummary(run=run, completed_at=generated_at)
