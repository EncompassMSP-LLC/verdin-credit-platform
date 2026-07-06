"""Operator-gated bureau unsupervised re-filing processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.bureau_refiling_models import BureauRefilingRunStatus
from api.modules.accounts.bureau_refiling_repository import BureauRefilingRunRepository
from api.modules.accounts.bureau_unsupervised_refiling_models import (
    BureauUnsupervisedRefilingRun,
    BureauUnsupervisedRefilingRunStatus,
)
from api.modules.accounts.bureau_unsupervised_refiling_repository import (
    BureauUnsupervisedRefilingRunRepository,
)
from api.modules.timeline.models import TimelineEvent
from api.modules.timeline.repository import TimelineRepository


@dataclass(frozen=True)
class BureauUnsupervisedRefilingRunSummary:
    run: BureauUnsupervisedRefilingRun
    completed_at: datetime


async def submit_bureau_unsupervised_refiling_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    bureau_refiling_run_id: uuid.UUID,
    refiling_summary: str,
    requested_by_user_id: uuid.UUID | None,
    unsupervised_repo: BureauUnsupervisedRefilingRunRepository | None = None,
    refiling_repo: BureauRefilingRunRepository | None = None,
) -> BureauUnsupervisedRefilingRunSummary:
    unsupervised_runs = unsupervised_repo or BureauUnsupervisedRefilingRunRepository(session)
    refilings = refiling_repo or BureauRefilingRunRepository(session)
    requested_at = unsupervised_runs.utcnow()

    refiling_run = await refilings.get_run_by_id(bureau_refiling_run_id)
    if refiling_run is None or refiling_run.organization_id != organization_id:
        raise ValueError("Bureau re-filing run not found")
    if refiling_run.status != BureauRefilingRunStatus.REFILED:
        raise ValueError("Bureau re-filing run is not refiled")

    run = await unsupervised_runs.create_run(
        organization_id=organization_id,
        bureau_refiling_run_id=refiling_run.id,
        account_id=refiling_run.account_id,
        case_id=refiling_run.case_id,
        bureau_target=refiling_run.bureau_target,
        status=BureauUnsupervisedRefilingRunStatus.PENDING_APPROVAL,
        refiling_summary=refiling_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return BureauUnsupervisedRefilingRunSummary(run=run, completed_at=requested_at)


async def approve_bureau_unsupervised_refiling_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    unsupervised_repo: BureauUnsupervisedRefilingRunRepository | None = None,
    timeline_repo: TimelineRepository | None = None,
) -> BureauUnsupervisedRefilingRunSummary:
    unsupervised_runs = unsupervised_repo or BureauUnsupervisedRefilingRunRepository(session)
    timeline = timeline_repo or TimelineRepository(session)
    approved_at = unsupervised_runs.utcnow()

    run = await unsupervised_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Bureau unsupervised re-filing run not found")
    if run.status != BureauUnsupervisedRefilingRunStatus.PENDING_APPROVAL:
        raise ValueError("Bureau unsupervised re-filing run is not pending approval")

    timeline_event = await timeline.append(
        TimelineEvent(
            organization_id=organization_id,
            case_id=run.case_id,
            event_type="bureau_unsupervised_refiling",
            event_category="compliance",
            title=f"Bureau unsupervised re-filing approved ({run.bureau_target})",
            description=run.refiling_summary,
            event_metadata={
                "run_id": str(run.id),
                "account_id": str(run.account_id),
                "bureau_refiling_run_id": str(run.bureau_refiling_run_id),
                "bureau_target": run.bureau_target,
                "approved_by_user_id": str(approved_by_user_id) if approved_by_user_id else None,
            },
            performed_by=approved_by_user_id,
            source_module="bureau_unsupervised_refiling",
        )
    )

    unsupervised_refiled_at = unsupervised_runs.utcnow()
    run.status = BureauUnsupervisedRefilingRunStatus.UNSUPERVISED_REFILED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.unsupervised_refiled_at = unsupervised_refiled_at
    run.timeline_event_id = timeline_event.id
    await session.flush()
    await session.refresh(run)
    return BureauUnsupervisedRefilingRunSummary(run=run, completed_at=unsupervised_refiled_at)
