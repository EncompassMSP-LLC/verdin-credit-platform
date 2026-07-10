"""Admin-gated public OAuth marketplace listing processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.org_admin.oauth_marketplace_publishing_models import (
    OAuthMarketplacePublishingRunStatus,
)
from api.modules.org_admin.oauth_marketplace_publishing_repository import (
    OAuthMarketplacePublishingRunRepository,
)
from api.modules.org_admin.public_oauth_marketplace_listing_models import (
    PublicOAuthMarketplaceListingRun,
    PublicOAuthMarketplaceListingRunStatus,
)
from api.modules.org_admin.public_oauth_marketplace_listing_repository import (
    PublicOAuthMarketplaceListingRunRepository,
)


@dataclass(frozen=True)
class PublicOAuthMarketplaceListingRunSummary:
    run: PublicOAuthMarketplaceListingRun
    completed_at: datetime


async def submit_public_oauth_marketplace_listing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    oauth_marketplace_publishing_run_id: uuid.UUID,
    listing_summary: str,
    public_listing_url: str | None,
    requested_by_user_id: uuid.UUID | None,
    listing_repo: PublicOAuthMarketplaceListingRunRepository | None = None,
    publishing_repo: OAuthMarketplacePublishingRunRepository | None = None,
) -> PublicOAuthMarketplaceListingRunSummary:
    listings = listing_repo or PublicOAuthMarketplaceListingRunRepository(session)
    publishing_runs = publishing_repo or OAuthMarketplacePublishingRunRepository(session)
    requested_at = listings.utcnow()

    publishing_run = await publishing_runs.get_run_by_id(oauth_marketplace_publishing_run_id)
    if publishing_run is None or publishing_run.organization_id != organization_id:
        raise ValueError("OAuth marketplace publishing run not found")
    if publishing_run.status != OAuthMarketplacePublishingRunStatus.APPROVED:
        raise ValueError("OAuth marketplace publishing run is not approved")

    run = await listings.create_run(
        organization_id=organization_id,
        oauth_marketplace_publishing_run_id=publishing_run.id,
        oauth_developer_app_id=publishing_run.oauth_developer_app_id,
        entity_id=publishing_run.entity_id,
        status=PublicOAuthMarketplaceListingRunStatus.PENDING_APPROVAL,
        listing_summary=listing_summary,
        marketplace_listing_slug=publishing_run.marketplace_listing_slug,
        public_listing_url=public_listing_url,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return PublicOAuthMarketplaceListingRunSummary(run=run, completed_at=requested_at)


async def approve_public_oauth_marketplace_listing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    listing_repo: PublicOAuthMarketplaceListingRunRepository | None = None,
) -> PublicOAuthMarketplaceListingRunSummary:
    listings = listing_repo or PublicOAuthMarketplaceListingRunRepository(session)
    approved_at = listings.utcnow()

    run = await listings.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Public OAuth marketplace listing run not found")
    if run.status != PublicOAuthMarketplaceListingRunStatus.PENDING_APPROVAL:
        raise ValueError("Public OAuth marketplace listing run is not pending approval")

    listed_at = listings.utcnow()
    run.status = PublicOAuthMarketplaceListingRunStatus.LISTED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.listed_at = listed_at
    await session.flush()
    await session.refresh(run)
    return PublicOAuthMarketplaceListingRunSummary(run=run, completed_at=listed_at)
