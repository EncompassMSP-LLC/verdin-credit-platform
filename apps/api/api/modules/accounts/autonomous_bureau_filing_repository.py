"""Repository for admin-gated autonomous bureau filing runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.autonomous_bureau_filing_models import (
    AutonomousBureauFilingRun,
    AutonomousBureauFilingRunStatus,
)


class AutonomousBureauFilingRunListFilters:
    def __init__(self, *, skip: int, limit: int, account_id: uuid.UUID | None = None) -> None:
        self.skip = skip
        self.limit = limit
        self.account_id = account_id


class AutonomousBureauFilingRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> AutonomousBureauFilingRun | None:
        result = await self._session.execute(
            select(AutonomousBureauFilingRun).where(AutonomousBureauFilingRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        bureau_live_api_run_id: uuid.UUID,
        account_id: uuid.UUID,
        case_id: uuid.UUID,
        bureau_target: str,
        status: AutonomousBureauFilingRunStatus,
        filing_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> AutonomousBureauFilingRun:
        run = AutonomousBureauFilingRun(
            organization_id=organization_id,
            bureau_live_api_run_id=bureau_live_api_run_id,
            account_id=account_id,
            case_id=case_id,
            bureau_target=bureau_target,
            status=status,
            filing_summary=filing_summary,
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
        filters: AutonomousBureauFilingRunListFilters,
    ) -> tuple[list[AutonomousBureauFilingRun], int]:
        base = (
            select(AutonomousBureauFilingRun)
            .where(AutonomousBureauFilingRun.organization_id == organization_id)
            .order_by(AutonomousBureauFilingRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(AutonomousBureauFilingRun)
            .where(AutonomousBureauFilingRun.organization_id == organization_id)
        )
        if filters.account_id is not None:
            base = base.where(AutonomousBureauFilingRun.account_id == filters.account_id)
            count_query = count_query.where(
                AutonomousBureauFilingRun.account_id == filters.account_id
            )

        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
