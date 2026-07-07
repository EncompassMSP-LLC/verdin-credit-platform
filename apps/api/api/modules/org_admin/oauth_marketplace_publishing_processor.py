"""Admin-gated OAuth marketplace publishing processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.org_admin.models import OAuthDeveloperAppStatus
from api.modules.org_admin.oauth_marketplace_publishing_models import (
    OAuthMarketplacePublishingRun,
    OAuthMarketplacePublishingRunStatus,
)
from api.modules.org_admin.oauth_marketplace_publishing_repository import (
    OAuthMarketplacePublishingRunRepository,
)
from api.modules.org_admin.repository import OrgAdminRepository


@dataclass(frozen=True)
class OAuthMarketplacePublishingRunSummary:
    run: OAuthMarketplacePublishingRun
    completed_at: datetime


async def submit_oauth_marketplace_publishing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    oauth_developer_app_id: uuid.UUID,
    publishing_summary: str,
    marketplace_listing_slug: str,
    requested_by_user_id: uuid.UUID | None,
    publishing_repo: OAuthMarketplacePublishingRunRepository | None = None,
    oauth_repo: OrgAdminRepository | None = None,
) -> OAuthMarketplacePublishingRunSummary:
    publishing_runs = publishing_repo or OAuthMarketplacePublishingRunRepository(session)
    oauth_apps = oauth_repo or OrgAdminRepository(session)
    requested_at = publishing_runs.utcnow()

    oauth_app = await oauth_apps.get_oauth_developer_app(
        oauth_developer_app_id,
        organization_id=organization_id,
    )
    if oauth_app is None:
        raise ValueError("OAuth developer app not found")
    if oauth_app.status != OAuthDeveloperAppStatus.APPROVED:
        raise ValueError("OAuth developer app is not approved")

    run = await publishing_runs.create_run(
        organization_id=organization_id,
        oauth_developer_app_id=oauth_app.id,
        entity_id=oauth_app.name,
        status=OAuthMarketplacePublishingRunStatus.PENDING_APPROVAL,
        publishing_summary=publishing_summary,
        marketplace_listing_slug=marketplace_listing_slug,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return OAuthMarketplacePublishingRunSummary(run=run, completed_at=requested_at)


async def approve_oauth_marketplace_publishing_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    publishing_repo: OAuthMarketplacePublishingRunRepository | None = None,
) -> OAuthMarketplacePublishingRunSummary:
    publishing_runs = publishing_repo or OAuthMarketplacePublishingRunRepository(session)
    approved_at = publishing_runs.utcnow()

    run = await publishing_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("OAuth marketplace publishing run not found")
    if run.status != OAuthMarketplacePublishingRunStatus.PENDING_APPROVAL:
        raise ValueError("OAuth marketplace publishing run is not pending approval")

    run.status = OAuthMarketplacePublishingRunStatus.APPROVED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    await session.flush()
    await session.refresh(run)
    return OAuthMarketplacePublishingRunSummary(run=run, completed_at=approved_at)
