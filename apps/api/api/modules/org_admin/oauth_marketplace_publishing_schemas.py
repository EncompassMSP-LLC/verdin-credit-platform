"""Pydantic schemas for admin-gated OAuth marketplace publishing scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.oauth_marketplace_publishing import (
    OAuthMarketplacePublishingStatus as PublishingGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.org_admin.oauth_marketplace_publishing_models import (
    OAuthMarketplacePublishingRun,
    OAuthMarketplacePublishingRunStatus,
)


class OAuthMarketplacePublishingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    public_oauth_developer_portal_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: PublishingGateStatus
    ) -> "OAuthMarketplacePublishingStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            public_oauth_developer_portal_ready=status.public_oauth_developer_portal_ready,
            blockers=list(status.blockers),
        )


class OAuthMarketplacePublishingSubmitRequest(BaseSchema):
    publishing_summary: str = Field(min_length=1, max_length=2000)
    marketplace_listing_slug: str = Field(min_length=1, max_length=255)


class OAuthMarketplacePublishingRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    oauth_developer_app_id: uuid.UUID
    entity_id: str
    status: OAuthMarketplacePublishingRunStatus
    publishing_summary: str
    marketplace_listing_slug: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: OAuthMarketplacePublishingRun
    ) -> "OAuthMarketplacePublishingRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            oauth_developer_app_id=run.oauth_developer_app_id,
            entity_id=run.entity_id,
            status=run.status,
            publishing_summary=run.publishing_summary,
            marketplace_listing_slug=run.marketplace_listing_slug,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            error_message=run.error_message,
        )


class OAuthMarketplacePublishingRunResultResponse(BaseSchema):
    completed_at: datetime
    run: OAuthMarketplacePublishingRunResponse


class OAuthMarketplacePublishingRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
