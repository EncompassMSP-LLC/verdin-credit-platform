"""Admin-gated fully autonomous bureau API filing processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.autonomous_bureau_filing_models import AutonomousBureauFilingRunStatus
from api.modules.accounts.autonomous_bureau_filing_repository import (
    AutonomousBureauFilingRunRepository,
)
from api.modules.accounts.fully_autonomous_bureau_api_filing_models import (
    FullyAutonomousBureauApiFilingRun,
    FullyAutonomousBureauApiFilingRunStatus,
)
from api.modules.accounts.fully_autonomous_bureau_api_filing_repository import (
    FullyAutonomousBureauApiFilingRunRepository,
)
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class FullyAutonomousBureauApiFilingRunSummary:
    run: FullyAutonomousBureauApiFilingRun
    completed_at: datetime


async def submit_fully_autonomous_bureau_api_filing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    autonomous_bureau_filing_run_id: uuid.UUID,
    api_filing_summary: str,
    execution_reference_id: str | None,
    requested_by_user_id: uuid.UUID | None,
    api_filing_repo: FullyAutonomousBureauApiFilingRunRepository | None = None,
    filing_repo: AutonomousBureauFilingRunRepository | None = None,
) -> FullyAutonomousBureauApiFilingRunSummary:
    api_filings = api_filing_repo or FullyAutonomousBureauApiFilingRunRepository(session)
    filings = filing_repo or AutonomousBureauFilingRunRepository(session)
    requested_at = api_filings.utcnow()

    filing_run = await filings.get_run_by_id(autonomous_bureau_filing_run_id)
    if filing_run is None or filing_run.organization_id != organization_id:
        raise ValueError("Autonomous bureau filing run not found")
    if filing_run.status != AutonomousBureauFilingRunStatus.FILED:
        raise ValueError("Autonomous bureau filing run is not filed")

    run = await api_filings.create_run(
        organization_id=organization_id,
        autonomous_bureau_filing_run_id=filing_run.id,
        account_id=filing_run.account_id,
        case_id=filing_run.case_id,
        bureau_target=filing_run.bureau_target,
        status=FullyAutonomousBureauApiFilingRunStatus.PENDING_APPROVAL,
        api_filing_summary=api_filing_summary,
        execution_reference_id=execution_reference_id,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return FullyAutonomousBureauApiFilingRunSummary(run=run, completed_at=requested_at)


async def approve_fully_autonomous_bureau_api_filing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    api_filing_repo: FullyAutonomousBureauApiFilingRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> FullyAutonomousBureauApiFilingRunSummary:
    api_filings = api_filing_repo or FullyAutonomousBureauApiFilingRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = api_filings.utcnow()

    run = await api_filings.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Fully autonomous bureau API filing run not found")
    if run.status != FullyAutonomousBureauApiFilingRunStatus.PENDING_APPROVAL:
        raise ValueError("Fully autonomous bureau API filing run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="fully_autonomous_bureau_api_filing",
            event_category="compliance",
            title=f"Fully autonomous bureau API filing executed ({run.bureau_target})",
            description=run.api_filing_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "autonomous_bureau_filing_run_id": str(run.autonomous_bureau_filing_run_id),
                "bureau_target": run.bureau_target,
                "execution_reference_id": run.execution_reference_id,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="fully_autonomous_bureau_api_filing",
        )
    )

    executed_at = api_filings.utcnow()
    run.status = FullyAutonomousBureauApiFilingRunStatus.EXECUTED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.executed_at = executed_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return FullyAutonomousBureauApiFilingRunSummary(run=run, completed_at=executed_at)
