"""Reporting materialized view refresh for the background worker."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from worker.reporting_tables import (
    REPORTING_MATERIALIZED_VIEWS,
    reporting_mv_refresh_runs_table,
)

STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
TRIGGER_SCHEDULED = "scheduled"


@dataclass(frozen=True, slots=True)
class ReportingMvRefreshResult:
    views_refreshed: int
    status: str


def run_reporting_mv_refresh(
    session: Session,
    *,
    organization_id: uuid.UUID | None = None,
    trigger_source: str = TRIGGER_SCHEDULED,
) -> ReportingMvRefreshResult:
    started_at = datetime.now(UTC)
    views_refreshed = 0
    error_message: str | None = None
    status = STATUS_COMPLETED

    try:
        for view_name in REPORTING_MATERIALIZED_VIEWS:
            session.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))
            views_refreshed += 1
    except Exception as exc:
        status = STATUS_FAILED
        error_message = str(exc)

    completed_at = datetime.now(UTC)
    now = datetime.now(UTC)
    session.execute(
        insert(reporting_mv_refresh_runs_table).values(
            id=uuid.uuid4(),
            organization_id=organization_id,
            trigger_source=trigger_source,
            status=status,
            views_refreshed=views_refreshed,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
            created_at=now,
            updated_at=now,
        )
    )

    return ReportingMvRefreshResult(views_refreshed=views_refreshed, status=status)
