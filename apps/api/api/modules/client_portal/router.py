"""Client portal authentication endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalLoginRequest,
    PortalMeResponse,
    PortalRefreshTokenRequest,
    PortalTokenResponse,
)
from api.modules.client_portal.service import ClientPortalAuthService

router = APIRouter(prefix="/portal/auth", tags=["Client Portal"])


def get_portal_auth_service(db: AsyncSession = Depends(get_db)) -> ClientPortalAuthService:
    return ClientPortalAuthService.from_session(db)


@router.post("/login", response_model=PortalTokenResponse)
async def portal_login(
    body: PortalLoginRequest,
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalTokenResponse:
    return await service.login(body)


@router.post("/refresh", response_model=PortalTokenResponse)
async def portal_refresh(
    body: PortalRefreshTokenRequest,
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalTokenResponse:
    return await service.refresh(body.refresh_token)


@router.get("/me", response_model=PortalMeResponse)
async def portal_me(
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalMeResponse:
    return await service.get_me(portal_user)
