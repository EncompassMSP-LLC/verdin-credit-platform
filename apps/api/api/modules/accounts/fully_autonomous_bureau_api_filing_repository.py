"""Repository for admin-gated fully autonomous bureau API filing runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.fully_autonomous_bureau_api_filing_models import (
    FullyAutonomousBureauApiFilingRun,
    FullyAutonomousBureauApiFilingRunStatus,
)


class FullyAutonomousBureauApiFilingRunListFilters:
    def __init__(self, *, skip: int, limit: int, account_id: uuid.UUID | None = None) -> None:
        self.skip = skip
        self.limit = limit
        self.account_id = account_id


class FullyAutonomousBureauApiFilingRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> FullyAutonomousBureauApiFilingRun | None:
        result = await self._session.execute(
            select(FullyAutonomousBureauApiFilingRun).where(
                FullyAutonomousBureauApiFilingRun.id == run_id
            )
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
        status: FullyAutonomousBureauApiFilingRunStatus,
        api_filing_summary: str,
        execution_reference_id: str | None,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> FullyAutonomousBureauApiFilingRun:
        run = FullyAutonomousBureauApiFilingRun(
            organization_id=organization_id,
            autonomous_bureau_filing_run_id=autonomous_bureau_filing_run_id,
            account_id=account_id,
            case_id=case_id,
            bureau_target=bureau_target,
            status=status,
            api_filing_summary=api_filing_summary,
            execution_reference_id=execution_reference_id,
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
        filters: FullyAutonomousBureauApiFilingRunListFilters,
    ) -> tuple[list[FullyAutonomousBureauApiFilingRun], int]:
        base = (
            select(FullyAutonomousBureauApiFilingRun)
            .where(FullyAutonomousBureauApiFilingRun.organization_id == organization_id)
            .order_by(FullyAutonomousBureauApiFilingRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(FullyAutonomousBureauApiFilingRun)
            .where(FullyAutonomousBureauApiFilingRun.organization_id == organization_id)
        )
        if filters.account_id is not None:
            base = base.where(FullyAutonomousBureauApiFilingRun.account_id == filters.account_id)
            count_query = count_query.where(
                FullyAutonomousBureauApiFilingRun.account_id == filters.account_id
            )

        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
