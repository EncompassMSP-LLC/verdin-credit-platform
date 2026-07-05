"""Admin-gated Stripe live Tax API processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.stripe_live_tax_api_models import (
    StripeLiveTaxApiRun,
    StripeLiveTaxApiRunStatus,
)
from api.modules.billing.stripe_live_tax_api_repository import StripeLiveTaxApiRunRepository
from api.modules.billing.tax_calculation_models import StripeTaxCalculationRunStatus
from api.modules.billing.tax_calculation_repository import StripeTaxCalculationRunRepository


@dataclass(frozen=True)
class StripeLiveTaxApiRunSummary:
    run: StripeLiveTaxApiRun
    completed_at: datetime


async def submit_stripe_live_tax_api_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    stripe_tax_calculation_run_id: uuid.UUID,
    invocation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    live_tax_repo: StripeLiveTaxApiRunRepository | None = None,
    tax_repo: StripeTaxCalculationRunRepository | None = None,
) -> StripeLiveTaxApiRunSummary:
    live_tax_runs = live_tax_repo or StripeLiveTaxApiRunRepository(session)
    tax_runs = tax_repo or StripeTaxCalculationRunRepository(session)
    requested_at = live_tax_runs.utcnow()

    tax_run = await tax_runs.get_run_by_id(stripe_tax_calculation_run_id)
    if tax_run is None or tax_run.organization_id != organization_id:
        raise ValueError("Stripe tax calculation run not found")
    if tax_run.status != StripeTaxCalculationRunStatus.CALCULATED:
        raise ValueError("Stripe tax calculation run is not calculated")

    run = await live_tax_runs.create_run(
        organization_id=organization_id,
        stripe_tax_calculation_run_id=tax_run.id,
        status=StripeLiveTaxApiRunStatus.PENDING_APPROVAL,
        invocation_summary=invocation_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return StripeLiveTaxApiRunSummary(run=run, completed_at=requested_at)


async def approve_stripe_live_tax_api_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    live_tax_repo: StripeLiveTaxApiRunRepository | None = None,
) -> StripeLiveTaxApiRunSummary:
    live_tax_runs = live_tax_repo or StripeLiveTaxApiRunRepository(session)
    approved_at = live_tax_runs.utcnow()

    run = await live_tax_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Stripe live Tax API run not found")
    if run.status != StripeLiveTaxApiRunStatus.PENDING_APPROVAL:
        raise ValueError("Stripe live Tax API run is not pending approval")

    invoked_at = live_tax_runs.utcnow()
    run.status = StripeLiveTaxApiRunStatus.INVOKED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.invoked_at = invoked_at
    await session.flush()
    await session.refresh(run)
    return StripeLiveTaxApiRunSummary(run=run, completed_at=invoked_at)
