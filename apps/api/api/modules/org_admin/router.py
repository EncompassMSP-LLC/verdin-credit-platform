"""Organization admin endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.org_admin.dependencies import (
    require_api_developer_portal_enabled,
    require_org_admin_enabled,
    require_public_oauth_developer_portal_enabled,
)
from api.modules.org_admin.oauth_marketplace_publishing_router import (
    oauth_marketplace_publishing_router,
)
from api.modules.org_admin.public_oauth_marketplace_listing_router import (
    public_oauth_marketplace_listing_router,
)
from api.modules.org_admin.schemas import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyRateLimitStatusResponse,
    ApiKeyResponse,
    ApiKeyRotateResponse,
    DeveloperPortalResponse,
    OAuthDeveloperAppCreate,
    OAuthDeveloperAppResponse,
    OrgAdminStatusResponse,
    OrganizationAdminSummary,
    OrganizationDisputeSettingsResponse,
    OrganizationDisputeSettingsUpdate,
)
from api.modules.org_admin.service import OrgAdminService

router = APIRouter(prefix="/org-admin", tags=["Organization Admin"])
router.include_router(oauth_marketplace_publishing_router)
router.include_router(public_oauth_marketplace_listing_router)


def get_org_admin_service(db: AsyncSession = Depends(get_db)) -> OrgAdminService:
    return OrgAdminService.from_session(db)


@router.get("/status", response_model=OrgAdminStatusResponse)
async def get_org_admin_status(
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> OrgAdminStatusResponse:
    return await service.get_status(current_user)


@router.get("/api-keys/rate-limit/status", response_model=ApiKeyRateLimitStatusResponse)
async def get_api_key_rate_limit_status_endpoint(
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> ApiKeyRateLimitStatusResponse:
    return await service.get_api_key_rate_limit_status(current_user)


@router.get("/organization", response_model=OrganizationAdminSummary)
async def get_organization_admin_summary(
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> OrganizationAdminSummary:
    return await service.get_organization_summary(current_user)


@router.get("/dispute-settings", response_model=OrganizationDisputeSettingsResponse)
async def get_organization_dispute_settings(
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> OrganizationDisputeSettingsResponse:
    return await service.get_dispute_settings(current_user)


@router.patch("/dispute-settings", response_model=OrganizationDisputeSettingsResponse)
async def update_organization_dispute_settings(
    body: OrganizationDisputeSettingsUpdate,
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> OrganizationDisputeSettingsResponse:
    return await service.update_dispute_settings(current_user, body)


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_organization_api_keys(
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> list[ApiKeyResponse]:
    return await service.list_api_keys(current_user)


@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_organization_api_key(
    body: ApiKeyCreate,
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> ApiKeyCreateResponse:
    return await service.create_api_key(current_user, body)


@router.get("/api-keys/{api_key_id}", response_model=ApiKeyResponse)
async def get_organization_api_key(
    api_key_id: uuid.UUID,
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> ApiKeyResponse:
    return await service.get_api_key(current_user, api_key_id)


@router.post("/api-keys/{api_key_id}/revoke", response_model=ApiKeyResponse)
async def revoke_organization_api_key(
    api_key_id: uuid.UUID,
    _: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> ApiKeyResponse:
    return await service.revoke_api_key(current_user, api_key_id)


@router.get(
    "/developer-portal",
    response_model=DeveloperPortalResponse,
    dependencies=[Depends(require_api_developer_portal_enabled)],
)
async def get_api_developer_portal(
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> DeveloperPortalResponse:
    return await service.get_developer_portal(current_user)


@router.post(
    "/api-keys/{api_key_id}/rotate",
    response_model=ApiKeyRotateResponse,
    dependencies=[Depends(require_api_developer_portal_enabled)],
)
async def rotate_organization_api_key(
    api_key_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> ApiKeyRotateResponse:
    return await service.rotate_api_key(current_user, api_key_id)


@router.get(
    "/developer-portal/oauth-apps",
    response_model=list[OAuthDeveloperAppResponse],
    dependencies=[Depends(require_public_oauth_developer_portal_enabled)],
)
async def list_oauth_developer_apps(
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> list[OAuthDeveloperAppResponse]:
    return await service.list_oauth_developer_apps(current_user)


@router.post(
    "/developer-portal/oauth-apps",
    response_model=OAuthDeveloperAppResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_public_oauth_developer_portal_enabled)],
)
async def create_oauth_developer_app(
    body: OAuthDeveloperAppCreate,
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> OAuthDeveloperAppResponse:
    return await service.create_oauth_developer_app(current_user, body)


@router.post(
    "/developer-portal/oauth-apps/{app_id}/approve",
    response_model=OAuthDeveloperAppResponse,
    dependencies=[Depends(require_public_oauth_developer_portal_enabled)],
)
async def approve_oauth_developer_app(
    app_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: OrgAdminService = Depends(get_org_admin_service),
) -> OAuthDeveloperAppResponse:
    return await service.approve_oauth_developer_app(current_user, app_id)
