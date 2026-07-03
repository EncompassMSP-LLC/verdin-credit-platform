"""Retention enforcement run audit repository."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.compliance.models import RetentionEnforcementRun


@dataclass(frozen=True, slots=True)
class EnforcementRunListFilters:
    organization_id: uuid.UUID
    skip: int = 0
    limit: int = 20


class RetentionEnforcementRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, run: RetentionEnforcementRun) -> RetentionEnforcementRun:
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        filters: EnforcementRunListFilters,
    ) -> tuple[list[RetentionEnforcementRun], int]:
        base = select(RetentionEnforcementRun).where(
            RetentionEnforcementRun.organization_id == filters.organization_id,
        )
        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        query = (
            base.order_by(RetentionEnforcementRun.started_at.desc())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def get_latest_started_at(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> datetime | None:
        query = (
            select(RetentionEnforcementRun.started_at)
            .where(RetentionEnforcementRun.organization_id == organization_id)
            .order_by(RetentionEnforcementRun.started_at.desc())
            .limit(1)
        )
        result = await self._session.execute(query)
        value = result.scalar_one_or_none()
        return value if isinstance(value, datetime) else None

    async def count_active_policies(self, *, organization_id: uuid.UUID) -> int:
        from api.modules.compliance.models import RetentionPolicy

        query = select(func.count()).where(
            RetentionPolicy.organization_id == organization_id,
            RetentionPolicy.deleted_at.is_(None),
            RetentionPolicy.is_active.is_(True),
        )
        return int((await self._session.execute(query)).scalar_one())
