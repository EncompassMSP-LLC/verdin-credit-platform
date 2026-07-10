"""Repository for public OAuth marketplace listing runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.org_admin.public_oauth_marketplace_listing_models import (
    PublicOAuthMarketplaceListingRun,
    PublicOAuthMarketplaceListingRunStatus,
)


class PublicOAuthMarketplaceListingRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class PublicOAuthMarketplaceListingRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> PublicOAuthMarketplaceListingRun | None:
        result = await self._session.execute(
            select(PublicOAuthMarketplaceListingRun).where(
                PublicOAuthMarketplaceListingRun.id == run_id
            )
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        oauth_marketplace_publishing_run_id: uuid.UUID,
        oauth_developer_app_id: uuid.UUID,
        entity_id: str,
        status: PublicOAuthMarketplaceListingRunStatus,
        listing_summary: str,
        marketplace_listing_slug: str,
        public_listing_url: str | None,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> PublicOAuthMarketplaceListingRun:
        run = PublicOAuthMarketplaceListingRun(
            organization_id=organization_id,
            oauth_marketplace_publishing_run_id=oauth_marketplace_publishing_run_id,
            oauth_developer_app_id=oauth_developer_app_id,
            entity_id=entity_id,
            status=status,
            listing_summary=listing_summary,
            marketplace_listing_slug=marketplace_listing_slug,
            public_listing_url=public_listing_url,
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
        filters: PublicOAuthMarketplaceListingRunListFilters,
    ) -> tuple[list[PublicOAuthMarketplaceListingRun], int]:
        base = (
            select(PublicOAuthMarketplaceListingRun)
            .where(PublicOAuthMarketplaceListingRun.organization_id == organization_id)
            .order_by(PublicOAuthMarketplaceListingRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(PublicOAuthMarketplaceListingRun)
            .where(PublicOAuthMarketplaceListingRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
