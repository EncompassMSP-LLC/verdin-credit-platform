"""Multi-IdP federation scaffold endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.dependencies import require_idp_federation_enabled
from api.modules.enterprise.federation_schemas import (
    IdpFederationProviderListResponse,
    IdpFederationProviderRegisterRequest,
    IdpFederationProviderResponse,
    IdpFederationStatusResponse,
)
from api.modules.enterprise.federation_service import IdpFederationService

federation_router = APIRouter(prefix="/federation", tags=["Enterprise Federation"])


def get_federation_service(db: AsyncSession = Depends(get_db)) -> IdpFederationService:
    return IdpFederationService.from_session(db)


@federation_router.get("/status", response_model=IdpFederationStatusResponse)
async def get_idp_federation_status(
    _: None = Depends(require_idp_federation_enabled),
    current_user: User = Depends(get_current_user),
    service: IdpFederationService = Depends(get_federation_service),
) -> IdpFederationStatusResponse:
    return await service.get_status_response(current_user)


@federation_router.get("/providers", response_model=IdpFederationProviderListResponse)
async def list_idp_federation_providers(
    _: None = Depends(require_idp_federation_enabled),
    current_user: User = Depends(get_current_user),
    service: IdpFederationService = Depends(get_federation_service),
) -> IdpFederationProviderListResponse:
    return await service.list_providers(current_user)


@federation_router.post(
    "/providers",
    response_model=IdpFederationProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_idp_federation_provider(
    body: IdpFederationProviderRegisterRequest,
    _: None = Depends(require_idp_federation_enabled),
    current_user: User = Depends(get_current_user),
    service: IdpFederationService = Depends(get_federation_service),
) -> IdpFederationProviderResponse:
    return await service.register_provider(current_user, body)
