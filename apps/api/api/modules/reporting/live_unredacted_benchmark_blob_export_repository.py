"""Repository for live unredacted benchmark blob export runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.reporting.live_unredacted_benchmark_blob_export_models import (
    LiveUnredactedBenchmarkBlobExportRun,
    LiveUnredactedBenchmarkBlobExportRunStatus,
)


class LiveUnredactedBenchmarkBlobExportRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class LiveUnredactedBenchmarkBlobExportRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> LiveUnredactedBenchmarkBlobExportRun | None:
        result = await self._session.execute(
            select(LiveUnredactedBenchmarkBlobExportRun).where(
                LiveUnredactedBenchmarkBlobExportRun.id == run_id
            )
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        unredacted_export_run_id: uuid.UUID,
        status: LiveUnredactedBenchmarkBlobExportRunStatus,
        export_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> LiveUnredactedBenchmarkBlobExportRun:
        run = LiveUnredactedBenchmarkBlobExportRun(
            organization_id=organization_id,
            unredacted_export_run_id=unredacted_export_run_id,
            status=status,
            export_summary=export_summary,
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
        filters: LiveUnredactedBenchmarkBlobExportRunListFilters,
    ) -> tuple[list[LiveUnredactedBenchmarkBlobExportRun], int]:
        base = (
            select(LiveUnredactedBenchmarkBlobExportRun)
            .where(LiveUnredactedBenchmarkBlobExportRun.organization_id == organization_id)
            .order_by(LiveUnredactedBenchmarkBlobExportRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(LiveUnredactedBenchmarkBlobExportRun)
            .where(LiveUnredactedBenchmarkBlobExportRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
