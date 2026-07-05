"""Repository for admin-gated Stripe invoice PDF generation runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.invoice_pdf_models import StripeInvoicePdfRun, StripeInvoicePdfRunStatus


class StripeInvoicePdfRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class StripeInvoicePdfRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> StripeInvoicePdfRun | None:
        result = await self._session.execute(
            select(StripeInvoicePdfRun).where(StripeInvoicePdfRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        collection_run_id: uuid.UUID,
        status: StripeInvoicePdfRunStatus,
        generation_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> StripeInvoicePdfRun:
        run = StripeInvoicePdfRun(
            organization_id=organization_id,
            collection_run_id=collection_run_id,
            status=status,
            generation_summary=generation_summary,
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
        filters: StripeInvoicePdfRunListFilters,
    ) -> tuple[list[StripeInvoicePdfRun], int]:
        base = (
            select(StripeInvoicePdfRun)
            .where(StripeInvoicePdfRun.organization_id == organization_id)
            .order_by(StripeInvoicePdfRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(StripeInvoicePdfRun)
            .where(StripeInvoicePdfRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
