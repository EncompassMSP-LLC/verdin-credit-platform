"""Repository for operator-gated bureau re-filing runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.bureau_refiling_models import BureauRefilingRun, BureauRefilingRunStatus


class BureauRefilingRunListFilters:
    def __init__(self, *, skip: int, limit: int, account_id: uuid.UUID | None = None) -> None:
        self.skip = skip
        self.limit = limit
        self.account_id = account_id


class BureauRefilingRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> BureauRefilingRun | None:
        result = await self._session.execute(
            select(BureauRefilingRun).where(BureauRefilingRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        autonomous_bureau_filing_run_id: uuid.UUID,
        account_id: uuid.UUID,
        case_id: uuid.UUID,
        bureau_target: str,
        status: BureauRefilingRunStatus,
        refiling_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> BureauRefilingRun:
        run = BureauRefilingRun(
            organization_id=organization_id,
            autonomous_bureau_filing_run_id=autonomous_bureau_filing_run_id,
            account_id=account_id,
            case_id=case_id,
            bureau_target=bureau_target,
            status=status,
            refiling_summary=refiling_summary,
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
        filters: BureauRefilingRunListFilters,
    ) -> tuple[list[BureauRefilingRun], int]:
        base = (
            select(BureauRefilingRun)
            .where(BureauRefilingRun.organization_id == organization_id)
            .order_by(BureauRefilingRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(BureauRefilingRun)
            .where(BureauRefilingRun.organization_id == organization_id)
        )
        if filters.account_id is not None:
            base = base.where(BureauRefilingRun.account_id == filters.account_id)
            count_query = count_query.where(BureauRefilingRun.account_id == filters.account_id)

        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
