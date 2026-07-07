"""Repository for admin-gated OAuth marketplace publishing runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.org_admin.oauth_marketplace_publishing_models import (
    OAuthMarketplacePublishingRun,
    OAuthMarketplacePublishingRunStatus,
)


class OAuthMarketplacePublishingRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class OAuthMarketplacePublishingRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> OAuthMarketplacePublishingRun | None:
        result = await self._session.execute(
            select(OAuthMarketplacePublishingRun).where(OAuthMarketplacePublishingRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        oauth_developer_app_id: uuid.UUID,
        entity_id: str,
        status: OAuthMarketplacePublishingRunStatus,
        publishing_summary: str,
        marketplace_listing_slug: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> OAuthMarketplacePublishingRun:
        run = OAuthMarketplacePublishingRun(
            organization_id=organization_id,
            oauth_developer_app_id=oauth_developer_app_id,
            entity_id=entity_id,
            status=status,
            publishing_summary=publishing_summary,
            marketplace_listing_slug=marketplace_listing_slug,
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
        filters: OAuthMarketplacePublishingRunListFilters,
    ) -> tuple[list[OAuthMarketplacePublishingRun], int]:
        base = (
            select(OAuthMarketplacePublishingRun)
            .where(OAuthMarketplacePublishingRun.organization_id == organization_id)
            .order_by(OAuthMarketplacePublishingRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(OAuthMarketplacePublishingRun)
            .where(OAuthMarketplacePublishingRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
