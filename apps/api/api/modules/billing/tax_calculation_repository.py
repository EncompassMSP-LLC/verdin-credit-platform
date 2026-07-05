"""Repository for admin-gated Stripe tax calculation runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.tax_calculation_models import (
    StripeTaxCalculationRun,
    StripeTaxCalculationRunStatus,
)


class StripeTaxCalculationRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class StripeTaxCalculationRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> StripeTaxCalculationRun | None:
        result = await self._session.execute(
            select(StripeTaxCalculationRun).where(StripeTaxCalculationRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        invoice_pdf_run_id: uuid.UUID,
        status: StripeTaxCalculationRunStatus,
        calculation_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> StripeTaxCalculationRun:
        run = StripeTaxCalculationRun(
            organization_id=organization_id,
            invoice_pdf_run_id=invoice_pdf_run_id,
            status=status,
            calculation_summary=calculation_summary,
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
        filters: StripeTaxCalculationRunListFilters,
    ) -> tuple[list[StripeTaxCalculationRun], int]:
        base = (
            select(StripeTaxCalculationRun)
            .where(StripeTaxCalculationRun.organization_id == organization_id)
            .order_by(StripeTaxCalculationRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(StripeTaxCalculationRun)
            .where(StripeTaxCalculationRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
