"""Predictive outcome snapshot and refresh repositories."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.reporting.predictive_models import (
    PredictiveOutcomeRefreshRun,
    PredictiveOutcomeRefreshStatus,
    PredictiveOutcomeSnapshot,
    PredictiveOutcomeTriggerSource,
)


class PredictiveOutcomeSnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_snapshot(
        self,
        organization_id: uuid.UUID,
    ) -> PredictiveOutcomeSnapshot | None:
        result = await self._session.execute(
            select(PredictiveOutcomeSnapshot).where(
                PredictiveOutcomeSnapshot.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_snapshot(
        self,
        *,
        organization_id: uuid.UUID,
        payload: dict[str, Any],
        refreshed_at: datetime,
    ) -> PredictiveOutcomeSnapshot:
        existing = await self.get_snapshot(organization_id)
        if existing is None:
            snapshot = PredictiveOutcomeSnapshot(
                organization_id=organization_id,
                payload=payload,
                refreshed_at=refreshed_at,
            )
            self._session.add(snapshot)
        else:
            existing.payload = payload
            existing.refreshed_at = refreshed_at
            snapshot = existing
        await self._session.flush()
        await self._session.refresh(snapshot)
        return snapshot


class PredictiveOutcomeRefreshRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        trigger_source: PredictiveOutcomeTriggerSource,
        status: PredictiveOutcomeRefreshStatus,
        started_at: datetime,
        completed_at: datetime,
        error_message: str | None = None,
    ) -> PredictiveOutcomeRefreshRun:
        run = PredictiveOutcomeRefreshRun(
            organization_id=organization_id,
            trigger_source=trigger_source,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def get_latest_refreshed_at(
        self,
        organization_id: uuid.UUID,
    ) -> datetime | None:
        result = await self._session.execute(
            select(func.max(PredictiveOutcomeRefreshRun.completed_at)).where(
                PredictiveOutcomeRefreshRun.organization_id == organization_id,
                PredictiveOutcomeRefreshRun.status == PredictiveOutcomeRefreshStatus.COMPLETED,
            )
        )
        value = result.scalar_one_or_none()
        return value if isinstance(value, datetime) else None
