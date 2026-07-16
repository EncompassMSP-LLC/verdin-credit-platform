"""Repository for bureau response ingestion audit runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.compliance.bureau_response_ingestion_models import (
    BureauResponseIngestionRun,
    BureauResponseIngestionRunStatus,
)

LIVE_POLLING_DEFERRAL_REASON = (
    "Live bureau response ingestion / polling is deferred to Version 17.0+ "
    "pending live bureau API access and legal/compliance sign-off. "
    "This run records operator intent only — no external bureau contact was made."
)


class BureauResponseIngestionRunListFilters:
    def __init__(
        self,
        *,
        skip: int,
        limit: int,
        case_id: uuid.UUID | None = None,
        account_id: uuid.UUID | None = None,
    ) -> None:
        self.skip = skip
        self.limit = limit
        self.case_id = case_id
        self.account_id = account_id


class BureauResponseIngestionRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> BureauResponseIngestionRun | None:
        result = await self._session.execute(
            select(BureauResponseIngestionRun).where(BureauResponseIngestionRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID | None,
        account_id: uuid.UUID | None,
        bureau_target: str,
        status: BureauResponseIngestionRunStatus,
        summary: str,
        deferral_reason: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> BureauResponseIngestionRun:
        run = BureauResponseIngestionRun(
            organization_id=organization_id,
            case_id=case_id,
            account_id=account_id,
            bureau_target=bureau_target,
            status=status,
            summary=summary,
            deferral_reason=deferral_reason,
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
        filters: BureauResponseIngestionRunListFilters,
    ) -> tuple[list[BureauResponseIngestionRun], int]:
        base = select(BureauResponseIngestionRun).where(
            BureauResponseIngestionRun.organization_id == organization_id
        )
        count_query = (
            select(func.count())
            .select_from(BureauResponseIngestionRun)
            .where(BureauResponseIngestionRun.organization_id == organization_id)
        )
        if filters.case_id is not None:
            base = base.where(BureauResponseIngestionRun.case_id == filters.case_id)
            count_query = count_query.where(BureauResponseIngestionRun.case_id == filters.case_id)
        if filters.account_id is not None:
            base = base.where(BureauResponseIngestionRun.account_id == filters.account_id)
            count_query = count_query.where(
                BureauResponseIngestionRun.account_id == filters.account_id
            )
        total = int((await self._session.execute(count_query)).scalar_one())
        query = (
            base.order_by(BureauResponseIngestionRun.requested_at.desc().nullslast())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total
