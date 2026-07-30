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
    PortalAcceptInviteRequest,
    PortalLoginRequest,
    PortalMeResponse,
    PortalPasswordResetConfirm,
    PortalPasswordResetRequest,
    PortalPasswordResetRequestResponse,
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


@router.post("/forgot-password", response_model=PortalPasswordResetRequestResponse)
async def portal_forgot_password(
    body: PortalPasswordResetRequest,
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalPasswordResetRequestResponse:
    return await service.request_password_reset(body)


@router.post("/reset-password", response_model=PortalTokenResponse)
async def portal_reset_password(
    body: PortalPasswordResetConfirm,
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalTokenResponse:
    return await service.confirm_password_reset(body)


@router.post("/accept-invite", response_model=PortalTokenResponse)
async def portal_accept_invite(
    body: PortalAcceptInviteRequest,
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalTokenResponse:
    return await service.accept_invite(body)


@router.get("/me", response_model=PortalMeResponse)
async def portal_me(
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalAuthService = Depends(get_portal_auth_service),
) -> PortalMeResponse:
    return await service.get_me(portal_user)
