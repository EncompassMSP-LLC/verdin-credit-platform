"""Operator-gated unsupervised autonomous filing loop processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.fully_autonomous_bureau_api_filing_models import (
    FullyAutonomousBureauApiFilingRunStatus,
)
from api.modules.accounts.fully_autonomous_bureau_api_filing_repository import (
    FullyAutonomousBureauApiFilingRunRepository,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_models import (
    UnsupervisedAutonomousFilingLoopRun,
    UnsupervisedAutonomousFilingLoopRunStatus,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_repository import (
    UnsupervisedAutonomousFilingLoopRunRepository,
)
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class UnsupervisedAutonomousFilingLoopRunSummary:
    run: UnsupervisedAutonomousFilingLoopRun
    completed_at: datetime


async def submit_unsupervised_autonomous_filing_loop_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    fully_autonomous_bureau_api_filing_run_id: uuid.UUID,
    loop_summary: str,
    loop_reference_id: str | None,
    requested_by_user_id: uuid.UUID | None,
    loop_repo: UnsupervisedAutonomousFilingLoopRunRepository | None = None,
    api_filing_repo: FullyAutonomousBureauApiFilingRunRepository | None = None,
) -> UnsupervisedAutonomousFilingLoopRunSummary:
    loops = loop_repo or UnsupervisedAutonomousFilingLoopRunRepository(session)
    api_filings = api_filing_repo or FullyAutonomousBureauApiFilingRunRepository(session)
    requested_at = loops.utcnow()

    api_filing_run = await api_filings.get_run_by_id(fully_autonomous_bureau_api_filing_run_id)
    if api_filing_run is None or api_filing_run.organization_id != organization_id:
        raise ValueError("Fully autonomous bureau API filing run not found")
    if api_filing_run.status != FullyAutonomousBureauApiFilingRunStatus.EXECUTED:
        raise ValueError("Fully autonomous bureau API filing run is not executed")

    run = await loops.create_run(
        organization_id=organization_id,
        fully_autonomous_bureau_api_filing_run_id=api_filing_run.id,
        account_id=api_filing_run.account_id,
        case_id=api_filing_run.case_id,
        bureau_target=api_filing_run.bureau_target,
        status=UnsupervisedAutonomousFilingLoopRunStatus.PENDING_APPROVAL,
        loop_summary=loop_summary,
        loop_reference_id=loop_reference_id,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return UnsupervisedAutonomousFilingLoopRunSummary(run=run, completed_at=requested_at)


async def approve_unsupervised_autonomous_filing_loop_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    loop_repo: UnsupervisedAutonomousFilingLoopRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> UnsupervisedAutonomousFilingLoopRunSummary:
    loops = loop_repo or UnsupervisedAutonomousFilingLoopRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = loops.utcnow()

    run = await loops.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Unsupervised autonomous filing loop run not found")
    if run.status != UnsupervisedAutonomousFilingLoopRunStatus.PENDING_APPROVAL:
        raise ValueError("Unsupervised autonomous filing loop run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="unsupervised_autonomous_filing_loop",
            event_category="compliance",
            title=f"Unsupervised autonomous filing loop approved ({run.bureau_target})",
            description=run.loop_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "fully_autonomous_bureau_api_filing_run_id": str(
                    run.fully_autonomous_bureau_api_filing_run_id
                ),
                "bureau_target": run.bureau_target,
                "loop_reference_id": run.loop_reference_id,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="unsupervised_autonomous_filing_loops",
        )
    )

    run.status = UnsupervisedAutonomousFilingLoopRunStatus.APPROVED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return UnsupervisedAutonomousFilingLoopRunSummary(run=run, completed_at=approved_at)
