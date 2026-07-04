"""SCIM 2.0 provisioning scaffold endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.dependencies import require_scim_provisioning_enabled
from api.modules.enterprise.scim_schemas import (
    ScimGroupListResponse,
    ScimGroupProvisionRequest,
    ScimGroupResourceResponse,
    ScimProvisioningStatusResponse,
    ScimUserListResponse,
    ScimUserProvisionRequest,
    ScimUserResourceResponse,
)
from api.modules.enterprise.scim_service import ScimProvisioningService

scim_router = APIRouter(prefix="/scim", tags=["Enterprise SCIM"])


def get_scim_service(db: AsyncSession = Depends(get_db)) -> ScimProvisioningService:
    return ScimProvisioningService.from_session(db)


@scim_router.get("/status", response_model=ScimProvisioningStatusResponse)
async def get_scim_provisioning_status(
    _: None = Depends(require_scim_provisioning_enabled),
    _current_user: User = Depends(get_current_user),
    service: ScimProvisioningService = Depends(get_scim_service),
) -> ScimProvisioningStatusResponse:
    return service.get_status_response()


@scim_router.post(
    "/v2/Users",
    response_model=ScimUserResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def provision_scim_user(
    body: ScimUserProvisionRequest,
    _: None = Depends(require_scim_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: ScimProvisioningService = Depends(get_scim_service),
) -> ScimUserResourceResponse:
    return await service.provision_user(current_user, body)


@scim_router.get("/v2/Users", response_model=ScimUserListResponse)
async def list_scim_users(
    _: None = Depends(require_scim_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: ScimProvisioningService = Depends(get_scim_service),
) -> ScimUserListResponse:
    return await service.list_users(current_user)


@scim_router.post(
    "/v2/Groups",
    response_model=ScimGroupResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def provision_scim_group(
    body: ScimGroupProvisionRequest,
    _: None = Depends(require_scim_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: ScimProvisioningService = Depends(get_scim_service),
) -> ScimGroupResourceResponse:
    return await service.provision_group(current_user, body)


@scim_router.get("/v2/Groups", response_model=ScimGroupListResponse)
async def list_scim_groups(
    _: None = Depends(require_scim_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: ScimProvisioningService = Depends(get_scim_service),
) -> ScimGroupListResponse:
    return await service.list_groups(current_user)
