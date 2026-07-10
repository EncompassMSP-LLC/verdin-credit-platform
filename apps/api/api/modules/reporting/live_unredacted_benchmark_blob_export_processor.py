"""Admin-gated live unredacted benchmark blob export processor scaffold."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.storage import DocumentStorage, async_put, get_document_storage
from api.modules.reporting.live_unredacted_benchmark_blob_export_models import (
    LiveUnredactedBenchmarkBlobExportRun,
    LiveUnredactedBenchmarkBlobExportRunStatus,
)
from api.modules.reporting.live_unredacted_benchmark_blob_export_repository import (
    LiveUnredactedBenchmarkBlobExportRunRepository,
)
from api.modules.reporting.unredacted_cross_org_benchmark_export_models import (
    UnredactedCrossOrgBenchmarkExportRunStatus,
)
from api.modules.reporting.unredacted_cross_org_benchmark_export_repository import (
    UnredactedCrossOrgBenchmarkExportRunRepository,
)

PLACEHOLDER_CONTENT_TYPE = "application/json"


@dataclass(frozen=True)
class LiveUnredactedBenchmarkBlobExportRunSummary:
    run: LiveUnredactedBenchmarkBlobExportRun
    completed_at: datetime


def _placeholder_artifact(*, parent_export_run_id: uuid.UUID, blob_run_id: uuid.UUID) -> bytes:
    payload = {
        "scaffold": True,
        "redacted": True,
        "parent_export_run_id": str(parent_export_run_id),
        "blob_export_run_id": str(blob_run_id),
        "note": "Placeholder artifact only — no tenant PII or unredacted benchmark payload",
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _storage_key(*, organization_id: uuid.UUID, parent_id: uuid.UUID, run_id: uuid.UUID) -> str:
    return f"{organization_id}/benchmark-exports/{parent_id}/{run_id}/export.json"


async def submit_live_unredacted_benchmark_blob_export_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    unredacted_export_run_id: uuid.UUID,
    export_summary: str,
    requested_by_user_id: uuid.UUID | None,
    blob_repo: LiveUnredactedBenchmarkBlobExportRunRepository | None = None,
    export_repo: UnredactedCrossOrgBenchmarkExportRunRepository | None = None,
) -> LiveUnredactedBenchmarkBlobExportRunSummary:
    blob_runs = blob_repo or LiveUnredactedBenchmarkBlobExportRunRepository(session)
    exports = export_repo or UnredactedCrossOrgBenchmarkExportRunRepository(session)
    requested_at = blob_runs.utcnow()

    parent = await exports.get_run_by_id(unredacted_export_run_id)
    if parent is None or parent.organization_id != organization_id:
        raise ValueError("Unredacted cross-org benchmark export run not found")
    if parent.status != UnredactedCrossOrgBenchmarkExportRunStatus.APPROVED:
        raise ValueError("Unredacted cross-org benchmark export run is not approved")

    run = await blob_runs.create_run(
        organization_id=organization_id,
        unredacted_export_run_id=parent.id,
        status=LiveUnredactedBenchmarkBlobExportRunStatus.PENDING_APPROVAL,
        export_summary=export_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return LiveUnredactedBenchmarkBlobExportRunSummary(run=run, completed_at=requested_at)


async def approve_live_unredacted_benchmark_blob_export_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    blob_repo: LiveUnredactedBenchmarkBlobExportRunRepository | None = None,
    storage: DocumentStorage | None = None,
) -> LiveUnredactedBenchmarkBlobExportRunSummary:
    blob_runs = blob_repo or LiveUnredactedBenchmarkBlobExportRunRepository(session)
    document_storage = storage or get_document_storage()
    exported_at = blob_runs.utcnow()

    run = await blob_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Live unredacted benchmark blob export run not found")
    if run.status != LiveUnredactedBenchmarkBlobExportRunStatus.PENDING_APPROVAL:
        raise ValueError("Live unredacted benchmark blob export run is not pending approval")

    artifact = _placeholder_artifact(
        parent_export_run_id=run.unredacted_export_run_id,
        blob_run_id=run.id,
    )
    storage_key = _storage_key(
        organization_id=organization_id,
        parent_id=run.unredacted_export_run_id,
        run_id=run.id,
    )
    await async_put(document_storage, storage_key, artifact, PLACEHOLDER_CONTENT_TYPE)

    run.status = LiveUnredactedBenchmarkBlobExportRunStatus.EXPORTED
    run.approved_by_user_id = approved_by_user_id
    run.exported_at = exported_at
    run.storage_key = storage_key
    run.content_type = PLACEHOLDER_CONTENT_TYPE
    run.byte_size = len(artifact)
    await session.flush()
    await session.refresh(run)
    return LiveUnredactedBenchmarkBlobExportRunSummary(run=run, completed_at=exported_at)
