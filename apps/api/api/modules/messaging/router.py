"""Staff secure messaging endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.messaging.schemas import (
    CaseMessageThreadResponse,
    MessageCreate,
    MessagingCenterStatusResponse,
    ThreadMessageResponse,
)
from api.modules.messaging.service import MessagingService

router = APIRouter(tags=["Messaging"])


def get_messaging_service(db: AsyncSession = Depends(get_db)) -> MessagingService:
    return MessagingService.from_session(db)


@router.get("/messaging/status", response_model=MessagingCenterStatusResponse)
async def get_messaging_status(
    current_user: User = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> MessagingCenterStatusResponse:
    return await service.get_status(current_user)


@router.get("/cases/{case_id}/message-thread", response_model=CaseMessageThreadResponse)
async def get_case_message_thread(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> CaseMessageThreadResponse:
    return await service.get_case_thread(current_user, case_id)


@router.post(
    "/cases/{case_id}/message-thread/messages",
    response_model=ThreadMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_case_message_thread_reply(
    case_id: uuid.UUID,
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> ThreadMessageResponse:
    return await service.post_staff_message(current_user, case_id, body)
