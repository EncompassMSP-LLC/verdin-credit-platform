"""Repository for native mobile app store distribution runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.native_mobile_app_store_distribution_models import (
    NativeMobileAppStoreDistributionRun,
    NativeMobileAppStoreDistributionRunStatus,
)


class NativeMobileAppStoreDistributionRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class NativeMobileAppStoreDistributionRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> NativeMobileAppStoreDistributionRun | None:
        result = await self._session.execute(
            select(NativeMobileAppStoreDistributionRun).where(
                NativeMobileAppStoreDistributionRun.id == run_id
            )
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        native_mobile_passkey_client_run_id: uuid.UUID,
        entity_id: str,
        status: NativeMobileAppStoreDistributionRunStatus,
        distribution_summary: str,
        platform: str,
        store_target: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> NativeMobileAppStoreDistributionRun:
        run = NativeMobileAppStoreDistributionRun(
            organization_id=organization_id,
            native_mobile_passkey_client_run_id=native_mobile_passkey_client_run_id,
            entity_id=entity_id,
            status=status,
            distribution_summary=distribution_summary,
            platform=platform,
            store_target=store_target,
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
        filters: NativeMobileAppStoreDistributionRunListFilters,
    ) -> tuple[list[NativeMobileAppStoreDistributionRun], int]:
        base = (
            select(NativeMobileAppStoreDistributionRun)
            .where(NativeMobileAppStoreDistributionRun.organization_id == organization_id)
            .order_by(NativeMobileAppStoreDistributionRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(NativeMobileAppStoreDistributionRun)
            .where(NativeMobileAppStoreDistributionRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
