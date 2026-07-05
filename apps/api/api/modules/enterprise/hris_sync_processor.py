"""Synchronous HRIS bidirectional sync run processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.hris_bidirectional_sync import compute_hris_sync_run_counts
from api.modules.enterprise.federation_metadata_repository import (
    SamlFederationMetadataUploadRepository,
)
from api.modules.enterprise.hris_sync_models import (
    HrisBidirectionalSyncRun,
    HrisBidirectionalSyncRunKind,
    HrisBidirectionalSyncRunStatus,
    HrisBidirectionalSyncTriggerSource,
)
from api.modules.enterprise.hris_sync_repository import HrisBidirectionalSyncRunRepository


@dataclass(frozen=True)
class HrisBidirectionalSyncRunSummary:
    run: HrisBidirectionalSyncRun
    completed_at: datetime


async def run_hris_bidirectional_sync(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_kind: HrisBidirectionalSyncRunKind,
    performed_by_user_id: uuid.UUID | None,
    run_repo: HrisBidirectionalSyncRunRepository | None = None,
    metadata_repo: SamlFederationMetadataUploadRepository | None = None,
) -> HrisBidirectionalSyncRunSummary:
    runs = run_repo or HrisBidirectionalSyncRunRepository(session)
    metadata = metadata_repo or SamlFederationMetadataUploadRepository(session)
    started_at = runs.utcnow()

    valid_upload_count = await metadata.count_valid_uploads(organization_id)
    records_synced, records_skipped = compute_hris_sync_run_counts(
        run_kind=run_kind.value,
        valid_metadata_upload_count=valid_upload_count,
    )

    run = await runs.create_run(
        organization_id=organization_id,
        run_kind=run_kind,
        trigger_source=HrisBidirectionalSyncTriggerSource.MANUAL,
        status=HrisBidirectionalSyncRunStatus.RUNNING,
        performed_by_user_id=performed_by_user_id,
        started_at=started_at,
    )

    if valid_upload_count <= 0:
        run.status = HrisBidirectionalSyncRunStatus.FAILED
        run.error_message = "Valid SAML federation metadata upload required before HRIS sync"
        run.completed_at = runs.utcnow()
        await session.flush()
        await session.refresh(run)
        return HrisBidirectionalSyncRunSummary(run=run, completed_at=run.completed_at)

    completed_at = runs.utcnow()
    run.status = HrisBidirectionalSyncRunStatus.COMPLETED
    run.records_synced = records_synced
    run.records_skipped = records_skipped
    run.completed_at = completed_at
    await session.flush()
    await session.refresh(run)
    return HrisBidirectionalSyncRunSummary(run=run, completed_at=completed_at)
