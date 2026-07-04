"""Batch document summary run repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.batch_summary_models import (
    BatchDocumentSummaryRun,
    BatchSummaryRunStatus,
)


class BatchDocumentSummaryRunListFilters:
    def __init__(self, *, organization_id: uuid.UUID, skip: int, limit: int) -> None:
        self.organization_id = organization_id
        self.skip = skip
        self.limit = limit


class BatchDocumentSummaryRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_run(self, run: BatchDocumentSummaryRun) -> BatchDocumentSummaryRun:
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def get_run(
        self,
        run_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> BatchDocumentSummaryRun | None:
        result = await self._session.execute(
            select(BatchDocumentSummaryRun).where(
                BatchDocumentSummaryRun.id == run_id,
                BatchDocumentSummaryRun.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def save_run(self, run: BatchDocumentSummaryRun) -> BatchDocumentSummaryRun:
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        filters: BatchDocumentSummaryRunListFilters,
    ) -> tuple[list[BatchDocumentSummaryRun], int]:
        base = select(BatchDocumentSummaryRun).where(
            BatchDocumentSummaryRun.organization_id == filters.organization_id,
        )
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(
            base.order_by(BatchDocumentSummaryRun.created_at.desc())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        return list(result.scalars().all()), total

    async def get_latest_completed_at(
        self,
        organization_id: uuid.UUID,
    ) -> BatchDocumentSummaryRun | None:
        result = await self._session.execute(
            select(BatchDocumentSummaryRun)
            .where(
                BatchDocumentSummaryRun.organization_id == organization_id,
                BatchDocumentSummaryRun.status == BatchSummaryRunStatus.COMPLETED,
            )
            .order_by(BatchDocumentSummaryRun.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
