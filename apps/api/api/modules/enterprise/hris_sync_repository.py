"""Repository for HRIS bidirectional sync runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.hris_sync_models import (
    HrisBidirectionalSyncRun,
    HrisBidirectionalSyncRunKind,
    HrisBidirectionalSyncRunStatus,
    HrisBidirectionalSyncTriggerSource,
)


class HrisBidirectionalSyncRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class HrisBidirectionalSyncRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> HrisBidirectionalSyncRun | None:
        result = await self._session.execute(
            select(HrisBidirectionalSyncRun).where(HrisBidirectionalSyncRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        run_kind: HrisBidirectionalSyncRunKind,
        trigger_source: HrisBidirectionalSyncTriggerSource,
        status: HrisBidirectionalSyncRunStatus,
        performed_by_user_id: uuid.UUID | None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        records_synced: int = 0,
        records_skipped: int = 0,
        error_message: str | None = None,
    ) -> HrisBidirectionalSyncRun:
        run = HrisBidirectionalSyncRun(
            organization_id=organization_id,
            run_kind=run_kind,
            trigger_source=trigger_source,
            status=status,
            performed_by_user_id=performed_by_user_id,
            started_at=started_at,
            completed_at=completed_at,
            records_synced=records_synced,
            records_skipped=records_skipped,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: HrisBidirectionalSyncRunListFilters,
    ) -> tuple[list[HrisBidirectionalSyncRun], int]:
        base = (
            select(HrisBidirectionalSyncRun)
            .where(HrisBidirectionalSyncRun.organization_id == organization_id)
            .order_by(HrisBidirectionalSyncRun.started_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(HrisBidirectionalSyncRun)
            .where(HrisBidirectionalSyncRun.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
