"""Admin-gated dispute bureau submission processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_bureau_submission_models import (
    DisputeBureauSubmissionRun,
    DisputeBureauSubmissionStatus,
)
from api.modules.accounts.dispute_bureau_submission_repository import (
    DisputeBureauSubmissionRunRepository,
)
from api.modules.accounts.dispute_filing_prep_models import DisputeFilingPrepStatus
from api.modules.accounts.dispute_filing_prep_repository import DisputeFilingPrepRunRepository
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class DisputeBureauSubmissionRunSummary:
    run: DisputeBureauSubmissionRun
    completed_at: datetime


async def submit_dispute_bureau_submission_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    filing_prep_run_id: uuid.UUID,
    submission_summary: str,
    requested_by_user_id: uuid.UUID | None,
    submission_repo: DisputeBureauSubmissionRunRepository | None = None,
    prep_repo: DisputeFilingPrepRunRepository | None = None,
) -> DisputeBureauSubmissionRunSummary:
    submissions = submission_repo or DisputeBureauSubmissionRunRepository(session)
    prep_runs = prep_repo or DisputeFilingPrepRunRepository(session)
    requested_at = submissions.utcnow()

    prep_run = await prep_runs.get_run_by_id(filing_prep_run_id)
    if prep_run is None or prep_run.organization_id != organization_id:
        raise ValueError("Dispute filing prep run not found")
    if prep_run.status != DisputeFilingPrepStatus.PREPARED:
        raise ValueError("Dispute filing prep run is not prepared")

    run = await submissions.create_run(
        organization_id=organization_id,
        account_id=prep_run.account_id,
        case_id=prep_run.case_id,
        filing_prep_run_id=prep_run.id,
        bureau_target=prep_run.bureau_target,
        status=DisputeBureauSubmissionStatus.PENDING_APPROVAL,
        submission_summary=submission_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return DisputeBureauSubmissionRunSummary(run=run, completed_at=requested_at)


async def approve_dispute_bureau_submission_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    submission_repo: DisputeBureauSubmissionRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> DisputeBureauSubmissionRunSummary:
    submissions = submission_repo or DisputeBureauSubmissionRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = submissions.utcnow()

    run = await submissions.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Dispute bureau submission run not found")
    if run.status != DisputeBureauSubmissionStatus.PENDING_APPROVAL:
        raise ValueError("Dispute bureau submission run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="dispute_bureau_submission",
            event_category="compliance",
            title=f"Dispute bureau submission approved ({run.bureau_target})",
            description=run.submission_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "filing_prep_run_id": str(run.filing_prep_run_id),
                "bureau_target": run.bureau_target,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="dispute_bureau_submission",
        )
    )

    submitted_at = submissions.utcnow()
    run.status = DisputeBureauSubmissionStatus.SUBMITTED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.submitted_at = submitted_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return DisputeBureauSubmissionRunSummary(run=run, completed_at=submitted_at)
