"""Repository for admin-gated Stripe live Tax API runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.stripe_live_tax_api_models import (
    StripeLiveTaxApiRun,
    StripeLiveTaxApiRunStatus,
)


class StripeLiveTaxApiRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class StripeLiveTaxApiRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> StripeLiveTaxApiRun | None:
        result = await self._session.execute(
            select(StripeLiveTaxApiRun).where(StripeLiveTaxApiRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        stripe_tax_calculation_run_id: uuid.UUID,
        status: StripeLiveTaxApiRunStatus,
        invocation_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> StripeLiveTaxApiRun:
        run = StripeLiveTaxApiRun(
            organization_id=organization_id,
            stripe_tax_calculation_run_id=stripe_tax_calculation_run_id,
            status=status,
            invocation_summary=invocation_summary,
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
        filters: StripeLiveTaxApiRunListFilters,
    ) -> tuple[list[StripeLiveTaxApiRun], int]:
        base = (
            select(StripeLiveTaxApiRun)
            .where(StripeLiveTaxApiRun.organization_id == organization_id)
            .order_by(StripeLiveTaxApiRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(StripeLiveTaxApiRun)
            .where(StripeLiveTaxApiRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
