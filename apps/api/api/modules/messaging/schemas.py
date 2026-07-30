"""Secure messaging schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.messaging.models import (
    MessageSenderRole,
    MessageThread,
    MessageThreadStatus,
    ThreadMessage,
)


class MessageCreate(BaseSchema):
    body: str = Field(min_length=1, max_length=10000)
    attachment_ids: list[uuid.UUID] = Field(default_factory=list, max_length=5)
    idempotency_key: str | None = Field(default=None, max_length=64)


class MessageAttachmentResponse(BaseSchema):
    id: uuid.UUID
    message_id: uuid.UUID | None
    document_id: uuid.UUID
    display_filename: str
    mime_type: str
    byte_size: int
    scan_status: str
    scan_detail: str | None
    downloadable: bool
    created_at: datetime


class ThreadMessageResponse(BaseSchema):
    id: uuid.UUID
    thread_id: uuid.UUID
    sender_role: MessageSenderRole
    portal_user_id: uuid.UUID | None
    staff_user_id: uuid.UUID | None
    body: str
    created_at: datetime
    attachments: list[MessageAttachmentResponse] = Field(default_factory=list)

    @classmethod
    def from_model(
        cls,
        message: ThreadMessage,
        *,
        attachments: list[MessageAttachmentResponse] | None = None,
    ) -> "ThreadMessageResponse":
        return cls(
            id=message.id,
            thread_id=message.thread_id,
            sender_role=message.sender_role,
            portal_user_id=message.portal_user_id,
            staff_user_id=message.staff_user_id,
            body=message.body,
            created_at=message.created_at,
            attachments=attachments or [],
        )


class CaseMessageThreadResponse(BaseSchema):
    case_id: uuid.UUID
    thread_id: uuid.UUID | None
    client_id: uuid.UUID | None
    status: MessageThreadStatus | None
    messages: list[ThreadMessageResponse]

    @classmethod
    def from_thread(
        cls,
        *,
        case_id: uuid.UUID,
        thread: MessageThread | None,
        messages: list[ThreadMessageResponse],
    ) -> "CaseMessageThreadResponse":
        if thread is None:
            return cls(
                case_id=case_id,
                thread_id=None,
                client_id=None,
                status=None,
                messages=[],
            )
        return cls(
            case_id=case_id,
            thread_id=thread.id,
            client_id=thread.client_id,
            status=thread.status,
            messages=messages,
        )


class MessagingCenterStatusResponse(BaseSchema):
    secure_messaging_enabled: bool
    thread_per_case: bool
    capabilities: list[str]
    deferred_capabilities: list[str]
