"""Client portal identity-theft confirmation endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.identity_theft_service import ClientPortalIdentityTheftService
from api.modules.client_portal.models import ClientPortalUser
from api.modules.documents.schemas import (
    ConfirmIdentityTheftAccountRequest,
    IdentityTheftAccountReviewResponse,
    IdentityTheftCaseCenterResponse,
)

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_portal_identity_theft_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalIdentityTheftService:
    return ClientPortalIdentityTheftService.from_session(db)


@router.get(
    "/{case_id}/identity-theft-center",
    response_model=IdentityTheftCaseCenterResponse,
)
async def get_portal_identity_theft_center(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalIdentityTheftService = Depends(get_portal_identity_theft_service),
) -> IdentityTheftCaseCenterResponse:
    return await service.get_identity_theft_center(portal_user, case_id)


@router.post(
    "/{case_id}/identity-theft/account-reviews",
    response_model=IdentityTheftAccountReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_portal_identity_theft_account(
    case_id: uuid.UUID,
    body: ConfirmIdentityTheftAccountRequest,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalIdentityTheftService = Depends(get_portal_identity_theft_service),
) -> IdentityTheftAccountReviewResponse:
    return await service.confirm_account(portal_user, case_id, body)
