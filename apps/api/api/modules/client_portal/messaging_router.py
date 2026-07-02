"""Client portal secure messaging endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.messaging_service import ClientPortalMessagingService
from api.modules.client_portal.models import ClientPortalUser
from api.modules.messaging.schemas import (
    CaseMessageThreadResponse,
    MessageCreate,
    ThreadMessageResponse,
)

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_portal_messaging_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalMessagingService:
    return ClientPortalMessagingService.from_session(db)


@router.get("/{case_id}/messages", response_model=CaseMessageThreadResponse)
async def list_portal_case_messages(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalMessagingService = Depends(get_portal_messaging_service),
) -> CaseMessageThreadResponse:
    return await service.list_case_messages(portal_user, case_id)


@router.post(
    "/{case_id}/messages",
    response_model=ThreadMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_portal_case_message(
    case_id: uuid.UUID,
    body: MessageCreate,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalMessagingService = Depends(get_portal_messaging_service),
) -> ThreadMessageResponse:
    return await service.send_case_message(portal_user, case_id, body)
