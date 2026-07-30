"""Client portal secure messaging endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.messaging_service import ClientPortalMessagingService
from api.modules.client_portal.models import ClientPortalUser
from api.modules.messaging.attachment_service import MessageAttachmentService
from api.modules.messaging.schemas import (
    CaseMessageThreadResponse,
    MessageAttachmentResponse,
    MessageCreate,
    ThreadMessageResponse,
)

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_portal_messaging_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalMessagingService:
    return ClientPortalMessagingService.from_session(db)


def get_attachment_service(db: AsyncSession = Depends(get_db)) -> MessageAttachmentService:
    return MessageAttachmentService.from_session(db)


@router.get("/{case_id}/messages", response_model=CaseMessageThreadResponse)
async def list_portal_case_messages(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalMessagingService = Depends(get_portal_messaging_service),
) -> CaseMessageThreadResponse:
    return await service.list_case_messages(portal_user, case_id)


@router.post(
    "/{case_id}/messages/attachments",
    response_model=MessageAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_portal_message_attachment(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: MessageAttachmentService = Depends(get_attachment_service),
) -> MessageAttachmentResponse:
    return await service.upload_for_portal(portal_user, case_id, file)


@router.delete(
    "/{case_id}/messages/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_portal_message_attachment(
    case_id: uuid.UUID,
    attachment_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: MessageAttachmentService = Depends(get_attachment_service),
) -> None:
    await service.delete_draft(
        organization_id=portal_user.organization_id,
        client_id=portal_user.client_id,
        case_id=case_id,
        attachment_id=attachment_id,
        actor_portal_user_id=portal_user.id,
    )


@router.get("/{case_id}/messages/attachments/{attachment_id}/download")
async def download_portal_message_attachment(
    case_id: uuid.UUID,
    attachment_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: MessageAttachmentService = Depends(get_attachment_service),
) -> Response:
    data, filename, mime_type = await service.download(
        organization_id=portal_user.organization_id,
        client_id=portal_user.client_id,
        case_id=case_id,
        attachment_id=attachment_id,
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
