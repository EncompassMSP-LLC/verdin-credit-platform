"""Admin-gated HRIS lifecycle sync processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.hris_lifecycle_models import (
    HrisLifecycleSyncRun,
    HrisLifecycleSyncRunStatus,
)
from api.modules.enterprise.hris_lifecycle_repository import HrisLifecycleSyncRunRepository
from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunStatus
from api.modules.enterprise.hris_sync_repository import HrisBidirectionalSyncRunRepository


@dataclass(frozen=True)
class HrisLifecycleSyncRunSummary:
    run: HrisLifecycleSyncRun
    completed_at: datetime


async def submit_hris_lifecycle_sync_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    hris_bidirectional_sync_run_id: uuid.UUID,
    lifecycle_summary: str,
    requested_by_user_id: uuid.UUID | None,
    lifecycle_repo: HrisLifecycleSyncRunRepository | None = None,
    sync_repo: HrisBidirectionalSyncRunRepository | None = None,
) -> HrisLifecycleSyncRunSummary:
    lifecycle_runs = lifecycle_repo or HrisLifecycleSyncRunRepository(session)
    sync_runs = sync_repo or HrisBidirectionalSyncRunRepository(session)
    requested_at = lifecycle_runs.utcnow()

    sync_run = await sync_runs.get_run_by_id(hris_bidirectional_sync_run_id)
    if sync_run is None or sync_run.organization_id != organization_id:
        raise ValueError("HRIS bidirectional sync run not found")
    if sync_run.status != HrisBidirectionalSyncRunStatus.COMPLETED:
        raise ValueError("HRIS bidirectional sync run is not completed")

    run = await lifecycle_runs.create_run(
        organization_id=organization_id,
        hris_bidirectional_sync_run_id=sync_run.id,
        run_kind=sync_run.run_kind,
        status=HrisLifecycleSyncRunStatus.PENDING_APPROVAL,
        lifecycle_summary=lifecycle_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return HrisLifecycleSyncRunSummary(run=run, completed_at=requested_at)


async def approve_hris_lifecycle_sync_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    lifecycle_repo: HrisLifecycleSyncRunRepository | None = None,
) -> HrisLifecycleSyncRunSummary:
    lifecycle_runs = lifecycle_repo or HrisLifecycleSyncRunRepository(session)
    approved_at = lifecycle_runs.utcnow()

    run = await lifecycle_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("HRIS lifecycle sync run not found")
    if run.status != HrisLifecycleSyncRunStatus.PENDING_APPROVAL:
        raise ValueError("HRIS lifecycle sync run is not pending approval")

    completed_at = lifecycle_runs.utcnow()
    run.status = HrisLifecycleSyncRunStatus.COMPLETED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.completed_at = completed_at
    await session.flush()
    await session.refresh(run)
    return HrisLifecycleSyncRunSummary(run=run, completed_at=completed_at)
