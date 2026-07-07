"""Repository for admin-gated mobile passkey readiness runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.mobile_passkey_readiness_models import (
    MobilePasskeyReadinessRun,
    MobilePasskeyReadinessRunStatus,
)


class MobilePasskeyReadinessRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class MobilePasskeyReadinessRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> MobilePasskeyReadinessRun | None:
        result = await self._session.execute(
            select(MobilePasskeyReadinessRun).where(MobilePasskeyReadinessRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        hris_passwordless_ui_run_id: uuid.UUID,
        entity_id: str,
        status: MobilePasskeyReadinessRunStatus,
        readiness_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> MobilePasskeyReadinessRun:
        run = MobilePasskeyReadinessRun(
            organization_id=organization_id,
            hris_passwordless_ui_run_id=hris_passwordless_ui_run_id,
            entity_id=entity_id,
            status=status,
            readiness_summary=readiness_summary,
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
        filters: MobilePasskeyReadinessRunListFilters,
    ) -> tuple[list[MobilePasskeyReadinessRun], int]:
        base = (
            select(MobilePasskeyReadinessRun)
            .where(MobilePasskeyReadinessRun.organization_id == organization_id)
            .order_by(MobilePasskeyReadinessRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(MobilePasskeyReadinessRun)
            .where(MobilePasskeyReadinessRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
