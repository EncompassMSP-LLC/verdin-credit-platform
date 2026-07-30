"""Message attachment domain models (LRP-302B)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class MessageAttachmentScanStatus(StrEnum):
    PENDING = "pending"
    CLEAN = "clean"
    REJECTED = "rejected"
    FAILED = "failed"


class MessageAttachmentUploader(StrEnum):
    STAFF = "staff"
    PORTAL_CLIENT = "portal_client"


class ThreadMessageAttachment(Base, TimestampMixin, SoftDeleteMixin):
    """Associates a case document with a secure message (or draft until send)."""

    __tablename__ = "thread_message_attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("thread_messages.id"), nullable=True, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False
    )
    uploaded_by_type: Mapped[MessageAttachmentUploader] = mapped_column(
        Enum(
            MessageAttachmentUploader,
            name="message_attachment_uploader",
            values_callable=lambda x: [e.value for e in x],
            create_constraint=False,
        ),
        nullable=False,
    )
    uploaded_by_staff_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    uploaded_by_portal_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_portal_users.id"), nullable=True
    )
    display_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    scan_status: Mapped[MessageAttachmentScanStatus] = mapped_column(
        Enum(
            MessageAttachmentScanStatus,
            name="message_attachment_scan_status",
            values_callable=lambda x: [e.value for e in x],
            create_constraint=False,
        ),
        nullable=False,
        default=MessageAttachmentScanStatus.PENDING,
    )
    scan_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
