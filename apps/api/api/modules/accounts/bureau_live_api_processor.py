"""Operator-gated bureau live API invocation processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.bureau_live_api_models import BureauLiveApiRun, BureauLiveApiRunStatus
from api.modules.accounts.bureau_live_api_repository import BureauLiveApiRunRepository
from api.modules.accounts.dispute_bureau_submission_models import DisputeBureauSubmissionStatus
from api.modules.accounts.dispute_bureau_submission_repository import (
    DisputeBureauSubmissionRunRepository,
)
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class BureauLiveApiRunSummary:
    run: BureauLiveApiRun
    completed_at: datetime


async def submit_bureau_live_api_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    bureau_submission_run_id: uuid.UUID,
    invocation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    live_api_repo: BureauLiveApiRunRepository | None = None,
    submission_repo: DisputeBureauSubmissionRunRepository | None = None,
) -> BureauLiveApiRunSummary:
    live_api_runs = live_api_repo or BureauLiveApiRunRepository(session)
    submissions = submission_repo or DisputeBureauSubmissionRunRepository(session)
    requested_at = live_api_runs.utcnow()

    submission_run = await submissions.get_run_by_id(bureau_submission_run_id)
    if submission_run is None or submission_run.organization_id != organization_id:
        raise ValueError("Dispute bureau submission run not found")
    if submission_run.status != DisputeBureauSubmissionStatus.SUBMITTED:
        raise ValueError("Dispute bureau submission run is not submitted")

    run = await live_api_runs.create_run(
        organization_id=organization_id,
        bureau_submission_run_id=submission_run.id,
        account_id=submission_run.account_id,
        case_id=submission_run.case_id,
        bureau_target=submission_run.bureau_target,
        status=BureauLiveApiRunStatus.PENDING_APPROVAL,
        invocation_summary=invocation_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return BureauLiveApiRunSummary(run=run, completed_at=requested_at)


async def approve_bureau_live_api_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    live_api_repo: BureauLiveApiRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> BureauLiveApiRunSummary:
    live_api_runs = live_api_repo or BureauLiveApiRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = live_api_runs.utcnow()

    run = await live_api_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Bureau live API run not found")
    if run.status != BureauLiveApiRunStatus.PENDING_APPROVAL:
        raise ValueError("Bureau live API run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="bureau_live_api_invocation",
            event_category="compliance",
            title=f"Bureau live API invocation approved ({run.bureau_target})",
            description=run.invocation_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "bureau_submission_run_id": str(run.bureau_submission_run_id),
                "bureau_target": run.bureau_target,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="bureau_live_api",
        )
    )

    invoked_at = live_api_runs.utcnow()
    run.status = BureauLiveApiRunStatus.INVOKED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.invoked_at = invoked_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return BureauLiveApiRunSummary(run=run, completed_at=invoked_at)
