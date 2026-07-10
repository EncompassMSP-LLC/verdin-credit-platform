"""Admin-gated unredacted cross-org benchmark export processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.reporting.cross_org_benchmark_models import CrossOrgBenchmarkRunStatus
from api.modules.reporting.cross_org_benchmark_repository import CrossOrgBenchmarkRepository
from api.modules.reporting.unredacted_cross_org_benchmark_export_models import (
    UnredactedCrossOrgBenchmarkExportRun,
    UnredactedCrossOrgBenchmarkExportRunStatus,
)
from api.modules.reporting.unredacted_cross_org_benchmark_export_repository import (
    UnredactedCrossOrgBenchmarkExportRunRepository,
)


@dataclass(frozen=True)
class UnredactedCrossOrgBenchmarkExportRunSummary:
    run: UnredactedCrossOrgBenchmarkExportRun
    completed_at: datetime


async def submit_unredacted_cross_org_benchmark_export_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    cross_org_benchmark_run_id: uuid.UUID,
    export_summary: str,
    export_reference_id: str | None,
    requested_by_user_id: uuid.UUID | None,
    export_repo: UnredactedCrossOrgBenchmarkExportRunRepository | None = None,
    benchmark_repo: CrossOrgBenchmarkRepository | None = None,
) -> UnredactedCrossOrgBenchmarkExportRunSummary:
    export_runs = export_repo or UnredactedCrossOrgBenchmarkExportRunRepository(session)
    benchmarks = benchmark_repo or CrossOrgBenchmarkRepository(session)
    requested_at = export_runs.utcnow()

    benchmark_run = await benchmarks.get_run_by_id(cross_org_benchmark_run_id)
    if benchmark_run is None:
        raise ValueError("Cross-org benchmark run not found")
    if benchmark_run.status != CrossOrgBenchmarkRunStatus.COMPLETED:
        raise ValueError("Cross-org benchmark run is not completed")

    run = await export_runs.create_run(
        organization_id=organization_id,
        cross_org_benchmark_run_id=benchmark_run.id,
        status=UnredactedCrossOrgBenchmarkExportRunStatus.PENDING_APPROVAL,
        export_summary=export_summary,
        export_reference_id=export_reference_id,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return UnredactedCrossOrgBenchmarkExportRunSummary(run=run, completed_at=requested_at)


async def approve_unredacted_cross_org_benchmark_export_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    export_repo: UnredactedCrossOrgBenchmarkExportRunRepository | None = None,
) -> UnredactedCrossOrgBenchmarkExportRunSummary:
    export_runs = export_repo or UnredactedCrossOrgBenchmarkExportRunRepository(session)
    approved_at = export_runs.utcnow()

    run = await export_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Unredacted cross-org benchmark export run not found")
    if run.status != UnredactedCrossOrgBenchmarkExportRunStatus.PENDING_APPROVAL:
        raise ValueError("Unredacted cross-org benchmark export run is not pending approval")

    run.status = UnredactedCrossOrgBenchmarkExportRunStatus.APPROVED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.export_reference_id = run.export_reference_id or f"unredacted-benchmark-export:{run.id}"
    await session.flush()
    await session.refresh(run)
    return UnredactedCrossOrgBenchmarkExportRunSummary(run=run, completed_at=approved_at)
