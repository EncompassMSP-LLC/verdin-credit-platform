"""Admin-gated OAuth marketplace publishing endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.org_admin.oauth_marketplace_publishing_dependencies import (
    require_oauth_marketplace_publishing_enabled,
)
from api.modules.org_admin.oauth_marketplace_publishing_schemas import (
    OAuthMarketplacePublishingRunListParams,
    OAuthMarketplacePublishingRunResponse,
    OAuthMarketplacePublishingRunResultResponse,
    OAuthMarketplacePublishingStatusResponse,
    OAuthMarketplacePublishingSubmitRequest,
)
from api.modules.org_admin.oauth_marketplace_publishing_service import (
    OAuthMarketplacePublishingService,
)

oauth_marketplace_publishing_router = APIRouter(
    prefix="/developer-portal/oauth-marketplace-publishing",
    tags=["OAuth Marketplace Publishing"],
)


def get_oauth_marketplace_publishing_service(
    db: AsyncSession = Depends(get_db),
) -> OAuthMarketplacePublishingService:
    return OAuthMarketplacePublishingService.from_session(db)


@oauth_marketplace_publishing_router.get(
    "/status",
    response_model=OAuthMarketplacePublishingStatusResponse,
)
async def get_oauth_marketplace_publishing_status_endpoint(
    _: None = Depends(require_oauth_marketplace_publishing_enabled),
    service: OAuthMarketplacePublishingService = Depends(get_oauth_marketplace_publishing_service),
) -> OAuthMarketplacePublishingStatusResponse:
    return service.get_status_response()


@oauth_marketplace_publishing_router.get(
    "/runs",
    response_model=PaginatedResponse[OAuthMarketplacePublishingRunResponse],
)
async def list_oauth_marketplace_publishing_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_oauth_marketplace_publishing_enabled),
    current_user: User = Depends(get_current_user),
    service: OAuthMarketplacePublishingService = Depends(get_oauth_marketplace_publishing_service),
) -> PaginatedResponse[OAuthMarketplacePublishingRunResponse]:
    params = OAuthMarketplacePublishingRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@oauth_marketplace_publishing_router.post(
    "/oauth-apps/{oauth_developer_app_id}/start",
    response_model=OAuthMarketplacePublishingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_oauth_marketplace_publishing_run_endpoint(
    oauth_developer_app_id: uuid.UUID,
    body: OAuthMarketplacePublishingSubmitRequest,
    _: None = Depends(require_oauth_marketplace_publishing_enabled),
    current_user: User = Depends(get_current_user),
    service: OAuthMarketplacePublishingService = Depends(get_oauth_marketplace_publishing_service),
) -> OAuthMarketplacePublishingRunResultResponse:
    return await service.submit_from_oauth_app(current_user, oauth_developer_app_id, body)


@oauth_marketplace_publishing_router.post(
    "/runs/{run_id}/approve",
    response_model=OAuthMarketplacePublishingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_oauth_marketplace_publishing_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_oauth_marketplace_publishing_enabled),
    current_user: User = Depends(get_current_user),
    service: OAuthMarketplacePublishingService = Depends(get_oauth_marketplace_publishing_service),
) -> OAuthMarketplacePublishingRunResultResponse:
    return await service.approve_run(current_user, run_id)
