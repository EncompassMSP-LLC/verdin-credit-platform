"""Repository for reporting materialized view refresh audit runs."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.reporting.materialized_models import (
    ReportingMvRefreshRun,
    ReportingMvRefreshStatus,
    ReportingMvTriggerSource,
)


@dataclass(frozen=True, slots=True)
class ReportingMvRefreshRunListFilters:
    skip: int
    limit: int


class ReportingMvRefreshRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID | None,
        trigger_source: ReportingMvTriggerSource,
        status: ReportingMvRefreshStatus,
        views_refreshed: int,
        started_at: datetime,
        completed_at: datetime,
        error_message: str | None,
    ) -> ReportingMvRefreshRun:
        run = ReportingMvRefreshRun(
            id=uuid.uuid4(),
            organization_id=organization_id,
            trigger_source=trigger_source,
            status=status,
            views_refreshed=views_refreshed,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def get_latest_started_at(self) -> datetime | None:
        result = await self._session.execute(
            select(func.max(ReportingMvRefreshRun.started_at)).where(
                ReportingMvRefreshRun.status == ReportingMvRefreshStatus.COMPLETED,
            )
        )
        value = result.scalar_one_or_none()
        return value if isinstance(value, datetime) else None

    async def list_runs(
        self,
        filters: ReportingMvRefreshRunListFilters,
    ) -> tuple[list[ReportingMvRefreshRun], int]:
        base = select(ReportingMvRefreshRun).order_by(ReportingMvRefreshRun.started_at.desc())
        total_result = await self._session.execute(
            select(func.count()).select_from(ReportingMvRefreshRun)
        )
        total = int(total_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
