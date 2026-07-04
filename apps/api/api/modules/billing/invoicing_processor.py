"""Synchronous billing invoicing run processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.billing_invoicing import compute_invoicing_run_counts
from api.modules.billing.invoicing_models import (
    BillingInvoicingRun,
    BillingInvoicingRunKind,
    BillingInvoicingRunStatus,
    BillingInvoicingTriggerSource,
)
from api.modules.billing.invoicing_repository import BillingInvoicingRunRepository
from api.modules.billing.models import SubscriptionStatus
from api.modules.billing.repository import BillingRepository


@dataclass(frozen=True)
class BillingInvoicingRunSummary:
    run: BillingInvoicingRun
    completed_at: datetime


async def run_billing_invoicing_cycle(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_kind: BillingInvoicingRunKind,
    performed_by_user_id: uuid.UUID | None,
    run_repo: BillingInvoicingRunRepository | None = None,
    billing_repo: BillingRepository | None = None,
) -> BillingInvoicingRunSummary:
    runs = run_repo or BillingInvoicingRunRepository(session)
    billing = billing_repo or BillingRepository(session)
    started_at = runs.utcnow()

    account = await billing.get_billing_account(organization_id)
    subscription_status = (
        account.subscription_status if account is not None else SubscriptionStatus.NONE
    )
    invoices_prepared, dunning_reminders_queued = compute_invoicing_run_counts(
        run_kind=run_kind.value,
        subscription_status=subscription_status,
        stripe_customer_configured=account is not None,
    )

    run = await runs.create_run(
        organization_id=organization_id,
        run_kind=run_kind,
        trigger_source=BillingInvoicingTriggerSource.MANUAL,
        status=BillingInvoicingRunStatus.RUNNING,
        performed_by_user_id=performed_by_user_id,
        started_at=started_at,
    )

    if account is None:
        run.status = BillingInvoicingRunStatus.FAILED
        run.error_message = "Billing customer not set up for organization"
        run.completed_at = runs.utcnow()
        await session.flush()
        await session.refresh(run)
        return BillingInvoicingRunSummary(run=run, completed_at=run.completed_at)

    completed_at = runs.utcnow()
    run.status = BillingInvoicingRunStatus.COMPLETED
    run.invoices_prepared = invoices_prepared
    run.dunning_reminders_queued = dunning_reminders_queued
    run.completed_at = completed_at
    await session.flush()
    await session.refresh(run)
    return BillingInvoicingRunSummary(run=run, completed_at=completed_at)
