"""Repository for billing invoicing and dunning runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.invoicing_models import (
    BillingInvoicingRun,
    BillingInvoicingRunKind,
    BillingInvoicingRunStatus,
    BillingInvoicingTriggerSource,
)


class BillingInvoicingRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class BillingInvoicingRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        run_kind: BillingInvoicingRunKind,
        trigger_source: BillingInvoicingTriggerSource,
        status: BillingInvoicingRunStatus,
        performed_by_user_id: uuid.UUID | None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        invoices_prepared: int = 0,
        dunning_reminders_queued: int = 0,
        error_message: str | None = None,
    ) -> BillingInvoicingRun:
        run = BillingInvoicingRun(
            organization_id=organization_id,
            run_kind=run_kind,
            trigger_source=trigger_source,
            status=status,
            performed_by_user_id=performed_by_user_id,
            started_at=started_at,
            completed_at=completed_at,
            invoices_prepared=invoices_prepared,
            dunning_reminders_queued=dunning_reminders_queued,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: BillingInvoicingRunListFilters,
    ) -> tuple[list[BillingInvoicingRun], int]:
        base = (
            select(BillingInvoicingRun)
            .where(BillingInvoicingRun.organization_id == organization_id)
            .order_by(BillingInvoicingRun.started_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(BillingInvoicingRun)
            .where(BillingInvoicingRun.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
