"""Admin-gated Stripe tax calculation processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.invoice_pdf_models import StripeInvoicePdfRunStatus
from api.modules.billing.invoice_pdf_repository import StripeInvoicePdfRunRepository
from api.modules.billing.tax_calculation_models import (
    StripeTaxCalculationRun,
    StripeTaxCalculationRunStatus,
)
from api.modules.billing.tax_calculation_repository import StripeTaxCalculationRunRepository


@dataclass(frozen=True)
class StripeTaxCalculationRunSummary:
    run: StripeTaxCalculationRun
    completed_at: datetime


async def submit_stripe_tax_calculation_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    invoice_pdf_run_id: uuid.UUID,
    calculation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    tax_repo: StripeTaxCalculationRunRepository | None = None,
    pdf_repo: StripeInvoicePdfRunRepository | None = None,
) -> StripeTaxCalculationRunSummary:
    tax_runs = tax_repo or StripeTaxCalculationRunRepository(session)
    pdf_runs = pdf_repo or StripeInvoicePdfRunRepository(session)
    requested_at = tax_runs.utcnow()

    pdf_run = await pdf_runs.get_run_by_id(invoice_pdf_run_id)
    if pdf_run is None or pdf_run.organization_id != organization_id:
        raise ValueError("Stripe invoice PDF run not found")
    if pdf_run.status != StripeInvoicePdfRunStatus.GENERATED:
        raise ValueError("Stripe invoice PDF run is not generated")

    run = await tax_runs.create_run(
        organization_id=organization_id,
        invoice_pdf_run_id=pdf_run.id,
        status=StripeTaxCalculationRunStatus.PENDING_APPROVAL,
        calculation_summary=calculation_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return StripeTaxCalculationRunSummary(run=run, completed_at=requested_at)


async def approve_stripe_tax_calculation_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    tax_repo: StripeTaxCalculationRunRepository | None = None,
) -> StripeTaxCalculationRunSummary:
    tax_runs = tax_repo or StripeTaxCalculationRunRepository(session)
    approved_at = tax_runs.utcnow()

    run = await tax_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Stripe tax calculation run not found")
    if run.status != StripeTaxCalculationRunStatus.PENDING_APPROVAL:
        raise ValueError("Stripe tax calculation run is not pending approval")

    calculated_at = tax_runs.utcnow()
    run.status = StripeTaxCalculationRunStatus.CALCULATED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.calculated_at = calculated_at
    await session.flush()
    await session.refresh(run)
    return StripeTaxCalculationRunSummary(run=run, completed_at=calculated_at)
