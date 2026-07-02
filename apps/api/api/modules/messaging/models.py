"""Secure messaging domain models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class MessageThreadStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class MessageSenderRole(StrEnum):
    PORTAL_CLIENT = "portal_client"
    STAFF = "staff"


class MessageThread(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "message_threads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True
    )
    status: Mapped[MessageThreadStatus] = mapped_column(
        Enum(
            MessageThreadStatus,
            name="message_thread_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=MessageThreadStatus.OPEN,
    )
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)

    messages: Mapped[list["ThreadMessage"]] = relationship(
        back_populates="thread",
        order_by="ThreadMessage.created_at.asc()",
    )


class ThreadMessage(Base):
    __tablename__ = "thread_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_threads.id"), nullable=False, index=True
    )
    sender_role: Mapped[MessageSenderRole] = mapped_column(
        Enum(
            MessageSenderRole,
            name="message_sender_role",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    portal_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_portal_users.id"), nullable=True
    )
    staff_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    thread: Mapped["MessageThread"] = relationship(back_populates="messages")
