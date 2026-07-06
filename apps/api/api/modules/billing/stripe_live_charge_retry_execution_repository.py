"""Repository for admin-gated Stripe live charge retry execution runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.stripe_live_charge_retry_execution_models import (
    StripeLiveChargeRetryExecutionRun,
    StripeLiveChargeRetryExecutionRunStatus,
)


class StripeLiveChargeRetryExecutionRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class StripeLiveChargeRetryExecutionRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> StripeLiveChargeRetryExecutionRun | None:
        result = await self._session.execute(
            select(StripeLiveChargeRetryExecutionRun).where(
                StripeLiveChargeRetryExecutionRun.id == run_id
            )
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        stripe_charge_retry_run_id: uuid.UUID,
        status: StripeLiveChargeRetryExecutionRunStatus,
        execution_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> StripeLiveChargeRetryExecutionRun:
        run = StripeLiveChargeRetryExecutionRun(
            organization_id=organization_id,
            stripe_charge_retry_run_id=stripe_charge_retry_run_id,
            status=status,
            execution_summary=execution_summary,
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
        filters: StripeLiveChargeRetryExecutionRunListFilters,
    ) -> tuple[list[StripeLiveChargeRetryExecutionRun], int]:
        base = (
            select(StripeLiveChargeRetryExecutionRun)
            .where(StripeLiveChargeRetryExecutionRun.organization_id == organization_id)
            .order_by(StripeLiveChargeRetryExecutionRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(StripeLiveChargeRetryExecutionRun)
            .where(StripeLiveChargeRetryExecutionRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
