"""Compliance-gated dispute filing prep processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_filing_prep_models import (
    DisputeFilingPrepRun,
    DisputeFilingPrepStatus,
)
from api.modules.accounts.dispute_filing_prep_repository import DisputeFilingPrepRunRepository
from api.modules.accounts.models import Account
from api.modules.accounts.repository import AccountRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class DisputeFilingPrepRunSummary:
    run: DisputeFilingPrepRun
    completed_at: datetime


async def submit_dispute_filing_prep_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    account_id: uuid.UUID,
    bureau_target: str,
    prep_summary: str,
    requested_by_user_id: uuid.UUID | None,
    account_repo: AccountRepository | None = None,
    run_repo: DisputeFilingPrepRunRepository | None = None,
) -> DisputeFilingPrepRunSummary:
    accounts = account_repo or AccountRepository(session)
    runs = run_repo or DisputeFilingPrepRunRepository(session)
    requested_at = runs.utcnow()

    account = await accounts.get_by_id(account_id, organization_id=organization_id)
    if account is None:
        raise ValueError("Account not found in organization")

    run = await runs.create_run(
        organization_id=organization_id,
        account_id=account.id,
        case_id=account.case_id,
        bureau_target=bureau_target,
        status=DisputeFilingPrepStatus.PENDING_APPROVAL,
        prep_summary=prep_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return DisputeFilingPrepRunSummary(run=run, completed_at=requested_at)


async def approve_dispute_filing_prep_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    run_repo: DisputeFilingPrepRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> DisputeFilingPrepRunSummary:
    runs = run_repo or DisputeFilingPrepRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = runs.utcnow()

    run = await runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Dispute filing prep run not found")
    if run.status != DisputeFilingPrepStatus.PENDING_APPROVAL:
        raise ValueError("Dispute filing prep run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="dispute_filing_prep",
            event_category="compliance",
            title=f"Dispute filing prep approved ({run.bureau_target})",
            description=run.prep_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "bureau_target": run.bureau_target,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="dispute_filing_prep",
        )
    )

    prepared_at = runs.utcnow()
    run.status = DisputeFilingPrepStatus.PREPARED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.prepared_at = prepared_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return DisputeFilingPrepRunSummary(run=run, completed_at=prepared_at)


def resolve_bureau_target(account: Account, requested: str | None) -> str:
    if requested is not None:
        return requested
    bureau = account.bureau
    return bureau.value if hasattr(bureau, "value") else str(bureau)
