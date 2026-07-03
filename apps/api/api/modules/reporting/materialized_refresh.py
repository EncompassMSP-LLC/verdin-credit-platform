"""Refresh reporting materialized views and record audit runs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.materialized_reporting import REPORTING_MATERIALIZED_VIEWS
from api.modules.reporting.materialized_models import (
    ReportingMvRefreshRun,
    ReportingMvRefreshStatus,
    ReportingMvTriggerSource,
)
from api.modules.reporting.materialized_repository import ReportingMvRefreshRunRepository


@dataclass(frozen=True, slots=True)
class MaterializedViewRefreshSummary:
    run: ReportingMvRefreshRun
    views_refreshed: int


async def refresh_reporting_materialized_views(
    session: AsyncSession,
    *,
    trigger_source: ReportingMvTriggerSource,
    organization_id: uuid.UUID | None = None,
    run_repo: ReportingMvRefreshRunRepository | None = None,
) -> MaterializedViewRefreshSummary:
    repository = run_repo or ReportingMvRefreshRunRepository(session)
    started_at = datetime.now(UTC)
    views_refreshed = 0
    error_message: str | None = None
    status = ReportingMvRefreshStatus.COMPLETED

    try:
        for view_name in REPORTING_MATERIALIZED_VIEWS:
            await session.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))
            views_refreshed += 1
    except Exception as exc:
        status = ReportingMvRefreshStatus.FAILED
        error_message = str(exc)

    completed_at = datetime.now(UTC)
    run = await repository.create_run(
        organization_id=organization_id,
        trigger_source=trigger_source,
        status=status,
        views_refreshed=views_refreshed,
        started_at=started_at,
        completed_at=completed_at,
        error_message=error_message,
    )
    return MaterializedViewRefreshSummary(run=run, views_refreshed=views_refreshed)


async def get_latest_successful_refresh_at(
    session: AsyncSession,
) -> datetime | None:
    result = await session.execute(
        select(func.max(ReportingMvRefreshRun.completed_at)).where(
            ReportingMvRefreshRun.status == ReportingMvRefreshStatus.COMPLETED,
        )
    )
    value = result.scalar_one_or_none()
    return value if isinstance(value, datetime) else None
