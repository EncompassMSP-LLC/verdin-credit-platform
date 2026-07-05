"""Operator-gated bureau re-filing processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.autonomous_bureau_filing_models import AutonomousBureauFilingRunStatus
from api.modules.accounts.autonomous_bureau_filing_repository import (
    AutonomousBureauFilingRunRepository,
)
from api.modules.accounts.bureau_refiling_models import BureauRefilingRun, BureauRefilingRunStatus
from api.modules.accounts.bureau_refiling_repository import BureauRefilingRunRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class BureauRefilingRunSummary:
    run: BureauRefilingRun
    completed_at: datetime


async def submit_bureau_refiling_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    autonomous_bureau_filing_run_id: uuid.UUID,
    refiling_summary: str,
    requested_by_user_id: uuid.UUID | None,
    refiling_repo: BureauRefilingRunRepository | None = None,
    filing_repo: AutonomousBureauFilingRunRepository | None = None,
) -> BureauRefilingRunSummary:
    refilings = refiling_repo or BureauRefilingRunRepository(session)
    filings = filing_repo or AutonomousBureauFilingRunRepository(session)
    requested_at = refilings.utcnow()

    filing_run = await filings.get_run_by_id(autonomous_bureau_filing_run_id)
    if filing_run is None or filing_run.organization_id != organization_id:
        raise ValueError("Autonomous bureau filing run not found")
    if filing_run.status != AutonomousBureauFilingRunStatus.FILED:
        raise ValueError("Autonomous bureau filing run is not filed")

    run = await refilings.create_run(
        organization_id=organization_id,
        autonomous_bureau_filing_run_id=filing_run.id,
        account_id=filing_run.account_id,
        case_id=filing_run.case_id,
        bureau_target=filing_run.bureau_target,
        status=BureauRefilingRunStatus.PENDING_APPROVAL,
        refiling_summary=refiling_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return BureauRefilingRunSummary(run=run, completed_at=requested_at)


async def approve_bureau_refiling_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    refiling_repo: BureauRefilingRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> BureauRefilingRunSummary:
    refilings = refiling_repo or BureauRefilingRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = refilings.utcnow()

    run = await refilings.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Bureau re-filing run not found")
    if run.status != BureauRefilingRunStatus.PENDING_APPROVAL:
        raise ValueError("Bureau re-filing run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="bureau_refiling",
            event_category="compliance",
            title=f"Bureau re-filing approved ({run.bureau_target})",
            description=run.refiling_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "autonomous_bureau_filing_run_id": str(run.autonomous_bureau_filing_run_id),
                "bureau_target": run.bureau_target,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="bureau_refiling",
        )
    )

    refiled_at = refilings.utcnow()
    run.status = BureauRefilingRunStatus.REFILED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.refiled_at = refiled_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return BureauRefilingRunSummary(run=run, completed_at=refiled_at)
