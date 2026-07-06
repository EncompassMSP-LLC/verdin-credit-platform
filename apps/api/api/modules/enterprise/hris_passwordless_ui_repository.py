"""Repository for admin-gated HRIS passwordless UI runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.hris_passwordless_ui_models import (
    HrisPasswordlessUiRun,
    HrisPasswordlessUiRunStatus,
)


class HrisPasswordlessUiRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class HrisPasswordlessUiRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> HrisPasswordlessUiRun | None:
        result = await self._session.execute(
            select(HrisPasswordlessUiRun).where(HrisPasswordlessUiRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        saml_passwordless_enrollment_run_id: uuid.UUID,
        entity_id: str,
        status: HrisPasswordlessUiRunStatus,
        ui_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> HrisPasswordlessUiRun:
        run = HrisPasswordlessUiRun(
            organization_id=organization_id,
            saml_passwordless_enrollment_run_id=saml_passwordless_enrollment_run_id,
            entity_id=entity_id,
            status=status,
            ui_summary=ui_summary,
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
        filters: HrisPasswordlessUiRunListFilters,
    ) -> tuple[list[HrisPasswordlessUiRun], int]:
        base = (
            select(HrisPasswordlessUiRun)
            .where(HrisPasswordlessUiRun.organization_id == organization_id)
            .order_by(HrisPasswordlessUiRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(HrisPasswordlessUiRun)
            .where(HrisPasswordlessUiRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
