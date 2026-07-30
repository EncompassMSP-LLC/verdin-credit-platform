"""Message attachment upload, scan, association, and download (LRP-302B)."""

from __future__ import annotations

import hashlib
import io
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import Headers
from verdin_event_bus import PlatformEvent
from verdin_event_types import EventCategory

from api.core.config import get_settings
from api.core.events import publish_platform_event
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.notification_service import ClientPortalNotificationService
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.service import DocumentService
from api.modules.documents.storage import async_get, async_put, get_document_storage
from api.modules.messaging.attachment_models import (
    MessageAttachmentScanStatus,
    MessageAttachmentUploader,
    ThreadMessageAttachment,
)
from api.modules.messaging.attachment_repository import MessageAttachmentRepository
from api.modules.messaging.attachment_scan import scan_attachment_bytes
from api.modules.messaging.models import ThreadMessage
from api.modules.messaging.schemas import MessageAttachmentResponse
from api.modules.notifications.models import NotificationCategory


def attachment_to_response(attachment: ThreadMessageAttachment) -> MessageAttachmentResponse:
    downloadable = attachment.scan_status is MessageAttachmentScanStatus.CLEAN
    return MessageAttachmentResponse(
        id=attachment.id,
        message_id=attachment.message_id,
        document_id=attachment.document_id,
        display_filename=attachment.display_filename,
        mime_type=attachment.mime_type,
        byte_size=attachment.byte_size,
        scan_status=attachment.scan_status.value,
        scan_detail=attachment.scan_detail if not downloadable else None,
        downloadable=downloadable,
        created_at=attachment.created_at,
    )


class MessageAttachmentService:
    def __init__(
        self,
        session: AsyncSession,
        attachment_repo: MessageAttachmentRepository | None = None,
        case_repo: CaseRepository | None = None,
        document_service: DocumentService | None = None,
    ) -> None:
        self._session = session
        self._attachments = attachment_repo or MessageAttachmentRepository(session)
        self._cases = case_repo or CaseRepository(session)
        self._documents = document_service or DocumentService.from_session(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> MessageAttachmentService:
        return cls(session)

    async def _require_case_client(
        self,
        *,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        expected_client_id: uuid.UUID | None = None,
    ) -> tuple[uuid.UUID, uuid.UUID]:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        if case.client_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case must be linked to a client before messaging attachments",
            )
        if expected_client_id is not None and case.client_id != expected_client_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case.id, case.client_id

    async def _enforce_rate_limit(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID | None = None,
        staff_user_id: uuid.UUID | None = None,
    ) -> None:
        settings = get_settings()
        count = await self._attachments.count_recent_uploads(
            organization_id=organization_id,
            portal_user_id=portal_user_id,
            staff_user_id=staff_user_id,
        )
        if count >= settings.message_attachment_upload_limit_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Attachment upload rate limit exceeded",
            )

    async def _store_document(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        data: bytes,
        mime_type: str,
        display_filename: str,
        created_by_id: uuid.UUID,
    ) -> Document:
        file_hash = hashlib.sha256(data).hexdigest()
        document_id = uuid.uuid4()
        storage_key = (
            f"{organization_id}/{case_id}/{document_id}/v1/" f"{display_filename.replace('/', '_')}"
        )
        storage = get_document_storage()
        await async_put(storage, storage_key, data, mime_type)
        now = datetime.now(UTC)
        document = Document(
            id=document_id,
            organization_id=organization_id,
            case_id=case_id,
            title=f"Message attachment: {display_filename}",
            description="Secure messaging attachment",
            file_name=display_filename,
            storage_key=storage_key,
            mime_type=mime_type,
            file_size=len(data),
            file_hash=file_hash,
            version_number=1,
            is_duplicate=False,
            processing_status="skipped",
        )
        self._session.add(document)
        await self._session.flush()
        version = DocumentVersion(
            id=uuid.uuid4(),
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            file_hash=file_hash,
            file_name=display_filename,
            mime_type=mime_type,
            file_size=len(data),
            created_at=now,
            created_by_id=created_by_id,
        )
        self._session.add(version)
        await self._session.flush()
        return document

    async def upload_for_portal(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        file: UploadFile,
    ) -> MessageAttachmentResponse:
        case_id, client_id = await self._require_case_client(
            case_id=case_id,
            organization_id=portal_user.organization_id,
            expected_client_id=portal_user.client_id,
        )
        await self._enforce_rate_limit(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
        )
        return await self._upload(
            organization_id=portal_user.organization_id,
            client_id=client_id,
            case_id=case_id,
            file=file,
            uploader_type=MessageAttachmentUploader.PORTAL_CLIENT,
            portal_user_id=portal_user.id,
            created_by_id=portal_user.id,
        )

    async def upload_for_staff(
        self,
        user: User,
        case_id: uuid.UUID,
        file: UploadFile,
    ) -> MessageAttachmentResponse:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        case_id, client_id = await self._require_case_client(
            case_id=case_id,
            organization_id=user.organization_id,
        )
        await self._enforce_rate_limit(
            organization_id=user.organization_id,
            staff_user_id=user.id,
        )
        return await self._upload(
            organization_id=user.organization_id,
            client_id=client_id,
            case_id=case_id,
            file=file,
            uploader_type=MessageAttachmentUploader.STAFF,
            staff_user_id=user.id,
            created_by_id=user.id,
        )

    async def _upload(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
        file: UploadFile,
        uploader_type: MessageAttachmentUploader,
        created_by_id: uuid.UUID,
        portal_user_id: uuid.UUID | None = None,
        staff_user_id: uuid.UUID | None = None,
    ) -> MessageAttachmentResponse:
        settings = get_settings()
        data = await file.read()
        scan = scan_attachment_bytes(
            data=data,
            declared_mime=file.content_type or "application/octet-stream",
            filename=file.filename,
            max_bytes=settings.document_max_upload_bytes,
            mode=settings.message_attachment_scan_mode,
        )
        if scan.status is MessageAttachmentScanStatus.REJECTED:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=scan.detail or "Attachment rejected",
            )
        if scan.status is MessageAttachmentScanStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=scan.detail or "Attachment scan unavailable",
            )

        # Re-wrap for document MIME gate (must match allowed messaging types).
        wrapped = UploadFile(
            filename=scan.display_filename,
            file=io.BytesIO(data),
            headers=Headers({"content-type": scan.mime_type}),
        )
        # Validate via DocumentService MIME gate without committing through its upload helpers.
        _data, content_type = await self._documents._read_upload(wrapped)
        document = await self._store_document(
            organization_id=organization_id,
            case_id=case_id,
            data=_data,
            mime_type=content_type,
            display_filename=scan.display_filename,
            created_by_id=created_by_id,
        )

        attachment = ThreadMessageAttachment(
            organization_id=organization_id,
            client_id=client_id,
            case_id=case_id,
            message_id=None,
            document_id=document.id,
            uploaded_by_type=uploader_type,
            uploaded_by_staff_user_id=staff_user_id,
            uploaded_by_portal_user_id=portal_user_id,
            display_filename=scan.display_filename,
            mime_type=content_type,
            byte_size=len(_data),
            scan_status=scan.status,
            scan_detail=scan.detail,
            scanned_at=datetime.now(UTC),
        )
        attachment = await self._attachments.create(attachment)
        await publish_platform_event(
            self._session,
            PlatformEvent(
                event_type="MESSAGE_ATTACHMENT_UPLOADED",
                event_category=EventCategory.MESSAGING.value,
                title="Message attachment uploaded",
                description="A secure messaging attachment was uploaded and scanned.",
                organization_id=organization_id,
                case_id=case_id,
                document_id=document.id,
                performed_by=staff_user_id,
                source_module="messaging.attachments",
                metadata={
                    "attachment_id": str(attachment.id),
                    "document_id": str(document.id),
                    "scan_status": attachment.scan_status.value,
                    "byte_size": attachment.byte_size,
                    "mime_type": attachment.mime_type,
                    "uploader_type": uploader_type.value,
                    "portal_user_id": str(portal_user_id) if portal_user_id else None,
                },
            ),
        )
        await self._session.commit()
        return attachment_to_response(attachment)

    async def delete_draft(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID | None,
        case_id: uuid.UUID,
        attachment_id: uuid.UUID,
        actor_portal_user_id: uuid.UUID | None = None,
        actor_staff_user_id: uuid.UUID | None = None,
    ) -> None:
        attachment = await self._attachments.get_by_id(
            attachment_id,
            organization_id=organization_id,
            client_id=client_id,
            case_id=case_id,
        )
        if attachment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )
        if attachment.message_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivered attachments cannot be removed",
            )
        if actor_portal_user_id is not None and (
            attachment.uploaded_by_portal_user_id != actor_portal_user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )
        if actor_staff_user_id is not None and (
            attachment.uploaded_by_staff_user_id != actor_staff_user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )
        await self._attachments.soft_delete(attachment)
        await publish_platform_event(
            self._session,
            PlatformEvent(
                event_type="MESSAGE_ATTACHMENT_DELETED",
                event_category=EventCategory.MESSAGING.value,
                title="Message attachment deleted",
                description="A draft messaging attachment was removed before send.",
                organization_id=organization_id,
                case_id=case_id,
                document_id=attachment.document_id,
                performed_by=actor_staff_user_id,
                source_module="messaging.attachments",
                metadata={
                    "attachment_id": str(attachment.id),
                    "document_id": str(attachment.document_id),
                },
            ),
        )
        await self._session.commit()

    async def associate_clean_attachments(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
        message_id: uuid.UUID,
        attachment_ids: list[uuid.UUID],
    ) -> list[ThreadMessageAttachment]:
        if not attachment_ids:
            return []
        if len(attachment_ids) != len(set(attachment_ids)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duplicate attachment ids",
            )
        rows = await self._attachments.list_by_ids(
            attachment_ids,
            organization_id=organization_id,
            client_id=client_id,
            case_id=case_id,
        )
        by_id = {row.id: row for row in rows}
        associated: list[ThreadMessageAttachment] = []
        for attachment_id in attachment_ids:
            row = by_id.get(attachment_id)
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Attachment not found",
                )
            if row.message_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Attachment already associated with a message",
                )
            if row.scan_status is not MessageAttachmentScanStatus.CLEAN:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Only clean attachments can be sent with a message",
                )
            row.message_id = message_id
            await self._attachments.save(row)
            associated.append(row)
            await publish_platform_event(
                self._session,
                PlatformEvent(
                    event_type="MESSAGE_ATTACHMENT_ASSOCIATED",
                    event_category=EventCategory.MESSAGING.value,
                    title="Message attachment associated",
                    description="An attachment was linked to a secure message.",
                    organization_id=organization_id,
                    case_id=case_id,
                    document_id=row.document_id,
                    source_module="messaging.attachments",
                    metadata={
                        "attachment_id": str(row.id),
                        "message_id": str(message_id),
                        "document_id": str(row.document_id),
                    },
                ),
            )
        return associated

    async def attachments_for_messages(
        self,
        messages: list[ThreadMessage],
        *,
        organization_id: uuid.UUID,
    ) -> dict[uuid.UUID, list[MessageAttachmentResponse]]:
        ids = [m.id for m in messages]
        rows = await self._attachments.list_for_messages(ids, organization_id=organization_id)
        grouped: dict[uuid.UUID, list[MessageAttachmentResponse]] = {mid: [] for mid in ids}
        for row in rows:
            if row.message_id is None:
                continue
            grouped.setdefault(row.message_id, []).append(attachment_to_response(row))
        return grouped

    async def download(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID | None,
        case_id: uuid.UUID,
        attachment_id: uuid.UUID,
        actor_staff_user_id: uuid.UUID | None = None,
    ) -> tuple[bytes, str, str]:
        attachment = await self._attachments.get_by_id(
            attachment_id,
            organization_id=organization_id,
            client_id=client_id,
            case_id=case_id,
        )
        if attachment is None or attachment.message_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )
        if attachment.scan_status is not MessageAttachmentScanStatus.CLEAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Attachment is not available for download",
            )
        document = await self._session.get(Document, attachment.document_id)
        if document is None or document.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )
        data = await async_get(get_document_storage(), document.storage_key)
        await publish_platform_event(
            self._session,
            PlatformEvent(
                event_type="MESSAGE_ATTACHMENT_DOWNLOAD_AUTHORIZED",
                event_category=EventCategory.MESSAGING.value,
                title="Message attachment download authorized",
                description="An authenticated download of a clean messaging attachment was authorized.",
                organization_id=organization_id,
                case_id=case_id,
                document_id=attachment.document_id,
                performed_by=actor_staff_user_id,
                source_module="messaging.attachments",
                metadata={
                    "attachment_id": str(attachment.id),
                    "document_id": str(attachment.document_id),
                    "message_id": str(attachment.message_id),
                },
            ),
        )
        await self._session.commit()
        return data, attachment.display_filename, attachment.mime_type

    async def notify_borrower_of_staff_message(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
        attachment_count: int,
    ) -> None:
        from api.modules.client_portal.repository import ClientPortalUserRepository

        portal_user = await ClientPortalUserRepository(self._session).get_by_client_id(
            client_id,
            organization_id=organization_id,
        )
        if portal_user is None:
            return
        body = "Your case team sent a secure message."
        if attachment_count:
            body = f"Your case team sent a secure message with {attachment_count} " "attachment(s)."
        await ClientPortalNotificationService.from_session(self._session).create(
            organization_id=organization_id,
            client_id=client_id,
            recipient_portal_user_id=portal_user.id,
            title="New secure message",
            body=body,
            category=NotificationCategory.SYSTEM,
            entity_type="case",
            entity_id=case_id,
            source_module="messaging",
            action_url="/portal/messages",
        )
