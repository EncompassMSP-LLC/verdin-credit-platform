"""Admin-gated Stripe charge retry processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.stripe_charge_retry_models import (
    StripeChargeRetryRun,
    StripeChargeRetryRunStatus,
)
from api.modules.billing.stripe_charge_retry_repository import StripeChargeRetryRunRepository
from api.modules.billing.stripe_live_tax_api_models import StripeLiveTaxApiRunStatus
from api.modules.billing.stripe_live_tax_api_repository import StripeLiveTaxApiRunRepository


@dataclass(frozen=True)
class StripeChargeRetryRunSummary:
    run: StripeChargeRetryRun
    completed_at: datetime


async def submit_stripe_charge_retry_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    stripe_live_tax_api_run_id: uuid.UUID,
    retry_summary: str,
    requested_by_user_id: uuid.UUID | None,
    retry_repo: StripeChargeRetryRunRepository | None = None,
    live_tax_repo: StripeLiveTaxApiRunRepository | None = None,
) -> StripeChargeRetryRunSummary:
    retries = retry_repo or StripeChargeRetryRunRepository(session)
    live_tax_runs = live_tax_repo or StripeLiveTaxApiRunRepository(session)
    requested_at = retries.utcnow()

    live_tax_run = await live_tax_runs.get_run_by_id(stripe_live_tax_api_run_id)
    if live_tax_run is None or live_tax_run.organization_id != organization_id:
        raise ValueError("Stripe live Tax API run not found")
    if live_tax_run.status != StripeLiveTaxApiRunStatus.INVOKED:
        raise ValueError("Stripe live Tax API run is not invoked")

    run = await retries.create_run(
        organization_id=organization_id,
        stripe_live_tax_api_run_id=live_tax_run.id,
        status=StripeChargeRetryRunStatus.PENDING_APPROVAL,
        retry_summary=retry_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return StripeChargeRetryRunSummary(run=run, completed_at=requested_at)


async def approve_stripe_charge_retry_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    retry_repo: StripeChargeRetryRunRepository | None = None,
) -> StripeChargeRetryRunSummary:
    retries = retry_repo or StripeChargeRetryRunRepository(session)
    approved_at = retries.utcnow()

    run = await retries.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Stripe charge retry run not found")
    if run.status != StripeChargeRetryRunStatus.PENDING_APPROVAL:
        raise ValueError("Stripe charge retry run is not pending approval")

    retried_at = retries.utcnow()
    run.status = StripeChargeRetryRunStatus.RETRIED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.retried_at = retried_at
    await session.flush()
    await session.refresh(run)
    return StripeChargeRetryRunSummary(run=run, completed_at=retried_at)
