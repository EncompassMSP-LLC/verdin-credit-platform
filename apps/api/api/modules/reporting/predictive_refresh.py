"""Refresh predictive outcome snapshots and record audit runs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.predictive_analytics import build_predictive_outcomes
from api.modules.reporting.predictive_models import (
    PredictiveOutcomeRefreshRun,
    PredictiveOutcomeRefreshStatus,
    PredictiveOutcomeTriggerSource,
)
from api.modules.reporting.predictive_repository import (
    PredictiveOutcomeRefreshRunRepository,
    PredictiveOutcomeSnapshotRepository,
)
from api.modules.reporting.repository import OperationsReportingRepository


@dataclass(frozen=True, slots=True)
class PredictiveOutcomeRefreshSummary:
    run: PredictiveOutcomeRefreshRun
    refreshed_at: datetime


async def refresh_predictive_outcomes(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    trigger_source: PredictiveOutcomeTriggerSource,
    snapshot_repo: PredictiveOutcomeSnapshotRepository | None = None,
    run_repo: PredictiveOutcomeRefreshRunRepository | None = None,
) -> PredictiveOutcomeRefreshSummary:
    reporting = OperationsReportingRepository(session)
    snapshots = snapshot_repo or PredictiveOutcomeSnapshotRepository(session)
    runs = run_repo or PredictiveOutcomeRefreshRunRepository(session)

    started_at = datetime.now(UTC)
    error_message: str | None = None
    status = PredictiveOutcomeRefreshStatus.COMPLETED
    refreshed_at = started_at

    try:
        raw = await reporting.get_historical_outcome_raw(organization_id)
        payload = build_predictive_outcomes(**raw, last_refreshed_at=refreshed_at)
        payload.pop("last_refreshed_at", None)
        await snapshots.upsert_snapshot(
            organization_id=organization_id,
            payload=payload,
            refreshed_at=refreshed_at,
        )
    except Exception as exc:
        status = PredictiveOutcomeRefreshStatus.FAILED
        error_message = str(exc)

    completed_at = datetime.now(UTC)
    run = await runs.create_run(
        organization_id=organization_id,
        trigger_source=trigger_source,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        error_message=error_message,
    )
    return PredictiveOutcomeRefreshSummary(run=run, refreshed_at=refreshed_at)
