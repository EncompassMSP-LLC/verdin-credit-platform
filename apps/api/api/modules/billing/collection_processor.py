"""Synchronous billing invoice collection run processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.billing_invoice_collection import compute_collection_run_counts
from api.modules.billing.collection_models import (
    BillingInvoiceCollectionRun,
    BillingInvoiceCollectionRunKind,
    BillingInvoiceCollectionRunStatus,
    BillingInvoiceCollectionTriggerSource,
)
from api.modules.billing.collection_repository import BillingInvoiceCollectionRunRepository
from api.modules.billing.models import SubscriptionStatus
from api.modules.billing.repository import BillingRepository


@dataclass(frozen=True)
class BillingInvoiceCollectionRunSummary:
    run: BillingInvoiceCollectionRun
    completed_at: datetime


async def run_billing_invoice_collection(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_kind: BillingInvoiceCollectionRunKind,
    performed_by_user_id: uuid.UUID | None,
    run_repo: BillingInvoiceCollectionRunRepository | None = None,
    billing_repo: BillingRepository | None = None,
) -> BillingInvoiceCollectionRunSummary:
    runs = run_repo or BillingInvoiceCollectionRunRepository(session)
    billing = billing_repo or BillingRepository(session)
    started_at = runs.utcnow()

    account = await billing.get_billing_account(organization_id)
    subscription_status = (
        account.subscription_status if account is not None else SubscriptionStatus.NONE
    )
    invoices_pdf_generated, payment_reminders_queued = compute_collection_run_counts(
        run_kind=run_kind.value,
        subscription_status=subscription_status,
        stripe_customer_configured=account is not None,
    )

    run = await runs.create_run(
        organization_id=organization_id,
        run_kind=run_kind,
        trigger_source=BillingInvoiceCollectionTriggerSource.MANUAL,
        status=BillingInvoiceCollectionRunStatus.RUNNING,
        performed_by_user_id=performed_by_user_id,
        started_at=started_at,
    )

    if account is None:
        run.status = BillingInvoiceCollectionRunStatus.FAILED
        run.error_message = "Billing customer not set up for organization"
        run.completed_at = runs.utcnow()
        await session.flush()
        await session.refresh(run)
        return BillingInvoiceCollectionRunSummary(run=run, completed_at=run.completed_at)

    completed_at = runs.utcnow()
    run.status = BillingInvoiceCollectionRunStatus.COMPLETED
    run.invoices_pdf_generated = invoices_pdf_generated
    run.payment_reminders_queued = payment_reminders_queued
    run.completed_at = completed_at
    await session.flush()
    await session.refresh(run)
    return BillingInvoiceCollectionRunSummary(run=run, completed_at=completed_at)
