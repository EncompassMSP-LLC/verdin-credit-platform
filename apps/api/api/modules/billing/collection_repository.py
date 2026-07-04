"""Repository for billing invoice collection runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.collection_models import (
    BillingInvoiceCollectionRun,
    BillingInvoiceCollectionRunKind,
    BillingInvoiceCollectionRunStatus,
    BillingInvoiceCollectionTriggerSource,
)


class BillingInvoiceCollectionRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class BillingInvoiceCollectionRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        run_kind: BillingInvoiceCollectionRunKind,
        trigger_source: BillingInvoiceCollectionTriggerSource,
        status: BillingInvoiceCollectionRunStatus,
        performed_by_user_id: uuid.UUID | None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        invoices_pdf_generated: int = 0,
        payment_reminders_queued: int = 0,
        error_message: str | None = None,
    ) -> BillingInvoiceCollectionRun:
        run = BillingInvoiceCollectionRun(
            organization_id=organization_id,
            run_kind=run_kind,
            trigger_source=trigger_source,
            status=status,
            performed_by_user_id=performed_by_user_id,
            started_at=started_at,
            completed_at=completed_at,
            invoices_pdf_generated=invoices_pdf_generated,
            payment_reminders_queued=payment_reminders_queued,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: BillingInvoiceCollectionRunListFilters,
    ) -> tuple[list[BillingInvoiceCollectionRun], int]:
        base = (
            select(BillingInvoiceCollectionRun)
            .where(BillingInvoiceCollectionRun.organization_id == organization_id)
            .order_by(BillingInvoiceCollectionRun.started_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(BillingInvoiceCollectionRun)
            .where(BillingInvoiceCollectionRun.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
