"""Repository for admin-gated unredacted cross-org benchmark export runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.reporting.unredacted_cross_org_benchmark_export_models import (
    UnredactedCrossOrgBenchmarkExportRun,
    UnredactedCrossOrgBenchmarkExportRunStatus,
)


class UnredactedCrossOrgBenchmarkExportRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class UnredactedCrossOrgBenchmarkExportRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> UnredactedCrossOrgBenchmarkExportRun | None:
        result = await self._session.execute(
            select(UnredactedCrossOrgBenchmarkExportRun).where(
                UnredactedCrossOrgBenchmarkExportRun.id == run_id
            )
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        cross_org_benchmark_run_id: uuid.UUID,
        status: UnredactedCrossOrgBenchmarkExportRunStatus,
        export_summary: str,
        export_reference_id: str | None,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> UnredactedCrossOrgBenchmarkExportRun:
        run = UnredactedCrossOrgBenchmarkExportRun(
            organization_id=organization_id,
            cross_org_benchmark_run_id=cross_org_benchmark_run_id,
            status=status,
            export_summary=export_summary,
            export_reference_id=export_reference_id,
            requested_by_user_id=requested_by_user_id,
            requested_at=requested_at,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: UnredactedCrossOrgBenchmarkExportRunListFilters,
    ) -> tuple[list[UnredactedCrossOrgBenchmarkExportRun], int]:
        base = (
            select(UnredactedCrossOrgBenchmarkExportRun)
            .where(UnredactedCrossOrgBenchmarkExportRun.organization_id == organization_id)
            .order_by(UnredactedCrossOrgBenchmarkExportRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(UnredactedCrossOrgBenchmarkExportRun)
            .where(UnredactedCrossOrgBenchmarkExportRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
