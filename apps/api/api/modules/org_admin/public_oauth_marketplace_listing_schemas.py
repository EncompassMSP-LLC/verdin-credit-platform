"""Pydantic schemas for public OAuth marketplace listing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.public_oauth_marketplace_listings import (
    PublicOAuthMarketplaceListingStatus as ListingGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.org_admin.public_oauth_marketplace_listing_models import (
    PublicOAuthMarketplaceListingRun,
    PublicOAuthMarketplaceListingRunStatus,
)


class PublicOAuthMarketplaceListingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    oauth_marketplace_publishing_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: ListingGateStatus
    ) -> "PublicOAuthMarketplaceListingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            oauth_marketplace_publishing_ready=status.oauth_marketplace_publishing_ready,
            blockers=list(status.blockers),
        )


class PublicOAuthMarketplaceListingSubmitRequest(BaseSchema):
    listing_summary: str = Field(min_length=1, max_length=2000)
    public_listing_url: str | None = Field(default=None, max_length=500)


class PublicOAuthMarketplaceListingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    oauth_marketplace_publishing_run_id: uuid.UUID
    oauth_developer_app_id: uuid.UUID
    entity_id: str
    status: PublicOAuthMarketplaceListingRunStatus
    listing_summary: str
    marketplace_listing_slug: str
    public_listing_url: str | None
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    listed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: PublicOAuthMarketplaceListingRun
    ) -> "PublicOAuthMarketplaceListingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            oauth_marketplace_publishing_run_id=run.oauth_marketplace_publishing_run_id,
            oauth_developer_app_id=run.oauth_developer_app_id,
            entity_id=run.entity_id,
            status=run.status,
            listing_summary=run.listing_summary,
            marketplace_listing_slug=run.marketplace_listing_slug,
            public_listing_url=run.public_listing_url,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            listed_at=run.listed_at,
            error_message=run.error_message,
        )


class PublicOAuthMarketplaceListingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: PublicOAuthMarketplaceListingRunResponse


class PublicOAuthMarketplaceListingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
