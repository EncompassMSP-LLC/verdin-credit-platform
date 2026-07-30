"""Staff secure messaging endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.messaging.attachment_service import MessageAttachmentService
from api.modules.messaging.permissions import MESSAGE_WRITE_ROLE
from api.modules.messaging.schemas import (
    CaseMessageThreadResponse,
    MessageAttachmentResponse,
    MessageCreate,
    MessagingCenterStatusResponse,
    ThreadMessageResponse,
)
from api.modules.messaging.service import MessagingService

router = APIRouter(tags=["Messaging"])


def get_messaging_service(db: AsyncSession = Depends(get_db)) -> MessagingService:
    return MessagingService.from_session(db)


def get_attachment_service(db: AsyncSession = Depends(get_db)) -> MessageAttachmentService:
    return MessageAttachmentService.from_session(db)


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
    "/cases/{case_id}/message-thread/attachments",
    response_model=MessageAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_case_message_attachment(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: MessageAttachmentService = Depends(get_attachment_service),
) -> MessageAttachmentResponse:
    if not has_permission(current_user.role, MESSAGE_WRITE_ROLE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to upload attachments",
        )
    return await service.upload_for_staff(current_user, case_id, file)


@router.delete(
    "/cases/{case_id}/message-thread/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_case_message_attachment(
    case_id: uuid.UUID,
    attachment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: MessageAttachmentService = Depends(get_attachment_service),
) -> None:
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization",
        )
    if not has_permission(current_user.role, MESSAGE_WRITE_ROLE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete attachments",
        )
    await service.delete_draft(
        organization_id=current_user.organization_id,
        client_id=None,
        case_id=case_id,
        attachment_id=attachment_id,
        actor_staff_user_id=current_user.id,
    )


@router.get("/cases/{case_id}/message-thread/attachments/{attachment_id}/download")
async def download_case_message_attachment(
    case_id: uuid.UUID,
    attachment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: MessageAttachmentService = Depends(get_attachment_service),
) -> Response:
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization",
        )
    data, filename, mime_type = await service.download(
        organization_id=current_user.organization_id,
        client_id=None,
        case_id=case_id,
        attachment_id=attachment_id,
        actor_staff_user_id=current_user.id,
    )
    return Response(
        content=data,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
        },
    )


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
