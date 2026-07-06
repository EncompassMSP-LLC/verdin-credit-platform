"""Admin-gated Stripe live charge retry execution processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.stripe_charge_retry_models import StripeChargeRetryRunStatus
from api.modules.billing.stripe_charge_retry_repository import StripeChargeRetryRunRepository
from api.modules.billing.stripe_live_charge_retry_execution_models import (
    StripeLiveChargeRetryExecutionRun,
    StripeLiveChargeRetryExecutionRunStatus,
)
from api.modules.billing.stripe_live_charge_retry_execution_repository import (
    StripeLiveChargeRetryExecutionRunRepository,
)


@dataclass(frozen=True)
class StripeLiveChargeRetryExecutionRunSummary:
    run: StripeLiveChargeRetryExecutionRun
    completed_at: datetime


async def submit_stripe_live_charge_retry_execution_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    stripe_charge_retry_run_id: uuid.UUID,
    execution_summary: str,
    requested_by_user_id: uuid.UUID | None,
    execution_repo: StripeLiveChargeRetryExecutionRunRepository | None = None,
    retry_repo: StripeChargeRetryRunRepository | None = None,
) -> StripeLiveChargeRetryExecutionRunSummary:
    executions = execution_repo or StripeLiveChargeRetryExecutionRunRepository(session)
    retries = retry_repo or StripeChargeRetryRunRepository(session)
    requested_at = executions.utcnow()

    retry_run = await retries.get_run_by_id(stripe_charge_retry_run_id)
    if retry_run is None or retry_run.organization_id != organization_id:
        raise ValueError("Stripe charge retry run not found")
    if retry_run.status != StripeChargeRetryRunStatus.RETRIED:
        raise ValueError("Stripe charge retry run is not retried")

    run = await executions.create_run(
        organization_id=organization_id,
        stripe_charge_retry_run_id=retry_run.id,
        status=StripeLiveChargeRetryExecutionRunStatus.PENDING_APPROVAL,
        execution_summary=execution_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return StripeLiveChargeRetryExecutionRunSummary(run=run, completed_at=requested_at)


async def approve_stripe_live_charge_retry_execution_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    execution_repo: StripeLiveChargeRetryExecutionRunRepository | None = None,
) -> StripeLiveChargeRetryExecutionRunSummary:
    executions = execution_repo or StripeLiveChargeRetryExecutionRunRepository(session)
    approved_at = executions.utcnow()

    run = await executions.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Stripe live charge retry execution run not found")
    if run.status != StripeLiveChargeRetryExecutionRunStatus.PENDING_APPROVAL:
        raise ValueError("Stripe live charge retry execution run is not pending approval")

    executed_at = executions.utcnow()
    run.status = StripeLiveChargeRetryExecutionRunStatus.EXECUTED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.executed_at = executed_at
    await session.flush()
    await session.refresh(run)
    return StripeLiveChargeRetryExecutionRunSummary(run=run, completed_at=executed_at)
