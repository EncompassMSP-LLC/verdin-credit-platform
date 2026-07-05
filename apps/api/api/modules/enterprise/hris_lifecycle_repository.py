"""Repository for admin-gated HRIS lifecycle sync runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.hris_lifecycle_models import (
    HrisLifecycleSyncRun,
    HrisLifecycleSyncRunStatus,
)
from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunKind


class HrisLifecycleSyncRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class HrisLifecycleSyncRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> HrisLifecycleSyncRun | None:
        result = await self._session.execute(
            select(HrisLifecycleSyncRun).where(HrisLifecycleSyncRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        hris_bidirectional_sync_run_id: uuid.UUID,
        run_kind: HrisBidirectionalSyncRunKind,
        status: HrisLifecycleSyncRunStatus,
        lifecycle_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> HrisLifecycleSyncRun:
        run = HrisLifecycleSyncRun(
            organization_id=organization_id,
            hris_bidirectional_sync_run_id=hris_bidirectional_sync_run_id,
            run_kind=run_kind,
            status=status,
            lifecycle_summary=lifecycle_summary,
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
        filters: HrisLifecycleSyncRunListFilters,
    ) -> tuple[list[HrisLifecycleSyncRun], int]:
        base = (
            select(HrisLifecycleSyncRun)
            .where(HrisLifecycleSyncRun.organization_id == organization_id)
            .order_by(HrisLifecycleSyncRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(HrisLifecycleSyncRun)
            .where(HrisLifecycleSyncRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
