"""Persisted dispute letter draft models."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base

if TYPE_CHECKING:
    from api.modules.accounts.models import Account
    from api.modules.cases.models import Case


class DisputeLetterStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SENT = "sent"
    VOID = "void"


class DisputeLetter(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "dispute_letters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True
    )
    recipient_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[DisputeLetterStatus] = mapped_column(
        Enum(
            DisputeLetterStatus,
            name="dispute_letter_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=DisputeLetterStatus.DRAFT,
        index=True,
    )
    template_id: Mapped[str] = mapped_column(String(100), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    disputed_items: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    requested_action: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_checklist: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    compliance_notes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    generated_by: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    account: Mapped[Account] = relationship()
    case: Mapped[Case] = relationship()
