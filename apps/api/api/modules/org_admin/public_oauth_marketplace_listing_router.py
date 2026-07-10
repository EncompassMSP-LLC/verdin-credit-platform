"""Admin-gated public OAuth marketplace listing endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.org_admin.public_oauth_marketplace_listing_dependencies import (
    require_public_oauth_marketplace_listings_enabled,
)
from api.modules.org_admin.public_oauth_marketplace_listing_schemas import (
    PublicOAuthMarketplaceListingRunListParams,
    PublicOAuthMarketplaceListingRunResponse,
    PublicOAuthMarketplaceListingRunResultResponse,
    PublicOAuthMarketplaceListingStatusResponse,
    PublicOAuthMarketplaceListingSubmitRequest,
)
from api.modules.org_admin.public_oauth_marketplace_listing_service import (
    PublicOAuthMarketplaceListingService,
)

public_oauth_marketplace_listing_router = APIRouter(
    prefix="/developer-portal/public-oauth-marketplace-listings",
    tags=["Public OAuth Marketplace Listings"],
)


def get_public_oauth_marketplace_listing_service(
    db: AsyncSession = Depends(get_db),
) -> PublicOAuthMarketplaceListingService:
    return PublicOAuthMarketplaceListingService.from_session(db)


@public_oauth_marketplace_listing_router.get(
    "/status",
    response_model=PublicOAuthMarketplaceListingStatusResponse,
)
async def get_public_oauth_marketplace_listing_status_endpoint(
    _: None = Depends(require_public_oauth_marketplace_listings_enabled),
    service: PublicOAuthMarketplaceListingService = Depends(
        get_public_oauth_marketplace_listing_service
    ),
) -> PublicOAuthMarketplaceListingStatusResponse:
    return service.get_status_response()


@public_oauth_marketplace_listing_router.get(
    "/runs",
    response_model=PaginatedResponse[PublicOAuthMarketplaceListingRunResponse],
)
async def list_public_oauth_marketplace_listing_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_public_oauth_marketplace_listings_enabled),
    current_user: User = Depends(get_current_user),
    service: PublicOAuthMarketplaceListingService = Depends(
        get_public_oauth_marketplace_listing_service
    ),
) -> PaginatedResponse[PublicOAuthMarketplaceListingRunResponse]:
    params = PublicOAuthMarketplaceListingRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@public_oauth_marketplace_listing_router.post(
    "/publishing-runs/{oauth_marketplace_publishing_run_id}/start",
    response_model=PublicOAuthMarketplaceListingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_public_oauth_marketplace_listing_run_endpoint(
    oauth_marketplace_publishing_run_id: uuid.UUID,
    body: PublicOAuthMarketplaceListingSubmitRequest,
    _: None = Depends(require_public_oauth_marketplace_listings_enabled),
    current_user: User = Depends(get_current_user),
    service: PublicOAuthMarketplaceListingService = Depends(
        get_public_oauth_marketplace_listing_service
    ),
) -> PublicOAuthMarketplaceListingRunResultResponse:
    return await service.submit_from_publishing_run(
        current_user, oauth_marketplace_publishing_run_id, body
    )


@public_oauth_marketplace_listing_router.post(
    "/runs/{run_id}/approve",
    response_model=PublicOAuthMarketplaceListingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_public_oauth_marketplace_listing_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_public_oauth_marketplace_listings_enabled),
    current_user: User = Depends(get_current_user),
    service: PublicOAuthMarketplaceListingService = Depends(
        get_public_oauth_marketplace_listing_service
    ),
) -> PublicOAuthMarketplaceListingRunResultResponse:
    return await service.approve_run(current_user, run_id)
