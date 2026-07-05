"""Admin-gated autonomous bureau filing processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.autonomous_bureau_filing_models import (
    AutonomousBureauFilingRun,
    AutonomousBureauFilingRunStatus,
)
from api.modules.accounts.autonomous_bureau_filing_repository import (
    AutonomousBureauFilingRunRepository,
)
from api.modules.accounts.bureau_live_api_models import BureauLiveApiRunStatus
from api.modules.accounts.bureau_live_api_repository import BureauLiveApiRunRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class AutonomousBureauFilingRunSummary:
    run: AutonomousBureauFilingRun
    completed_at: datetime


async def submit_autonomous_bureau_filing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    bureau_live_api_run_id: uuid.UUID,
    filing_summary: str,
    requested_by_user_id: uuid.UUID | None,
    filing_repo: AutonomousBureauFilingRunRepository | None = None,
    live_api_repo: BureauLiveApiRunRepository | None = None,
) -> AutonomousBureauFilingRunSummary:
    filings = filing_repo or AutonomousBureauFilingRunRepository(session)
    live_api_runs = live_api_repo or BureauLiveApiRunRepository(session)
    requested_at = filings.utcnow()

    live_api_run = await live_api_runs.get_run_by_id(bureau_live_api_run_id)
    if live_api_run is None or live_api_run.organization_id != organization_id:
        raise ValueError("Bureau live API run not found")
    if live_api_run.status != BureauLiveApiRunStatus.INVOKED:
        raise ValueError("Bureau live API run is not invoked")

    run = await filings.create_run(
        organization_id=organization_id,
        bureau_live_api_run_id=live_api_run.id,
        account_id=live_api_run.account_id,
        case_id=live_api_run.case_id,
        bureau_target=live_api_run.bureau_target,
        status=AutonomousBureauFilingRunStatus.PENDING_APPROVAL,
        filing_summary=filing_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return AutonomousBureauFilingRunSummary(run=run, completed_at=requested_at)


async def approve_autonomous_bureau_filing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    filing_repo: AutonomousBureauFilingRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> AutonomousBureauFilingRunSummary:
    filings = filing_repo or AutonomousBureauFilingRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = filings.utcnow()

    run = await filings.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Autonomous bureau filing run not found")
    if run.status != AutonomousBureauFilingRunStatus.PENDING_APPROVAL:
        raise ValueError("Autonomous bureau filing run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="autonomous_bureau_filing",
            event_category="compliance",
            title=f"Autonomous bureau filing approved ({run.bureau_target})",
            description=run.filing_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "bureau_live_api_run_id": str(run.bureau_live_api_run_id),
                "bureau_target": run.bureau_target,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="autonomous_bureau_filing",
        )
    )

    filed_at = filings.utcnow()
    run.status = AutonomousBureauFilingRunStatus.FILED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.filed_at = filed_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return AutonomousBureauFilingRunSummary(run=run, completed_at=filed_at)
