"""SQLAlchemy model for Intelligent Letter Draft Builder (LRP-406)."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.database.base import Base


class LetterDraftWorkflowStatus(str, enum.Enum):
    AI_DRAFT_CREATED = "ai_draft_created"
    STAFF_REVIEW = "staff_review"
    CLIENT_REVIEW = "client_review"
    APPROVED = "approved"
    READY_TO_SEND = "ready_to_send"
    SENT_RECORDED = "sent_recorded"
    DELIVERY_CONFIRMED = "delivery_confirmed"
    RESPONSE_RECEIVED = "response_received"


class IntelligentLetterDraft(Base):
    __tablename__ = "intelligent_letter_drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    template_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    workflow_status: Mapped[LetterDraftWorkflowStatus] = mapped_column(
        Enum(
            LetterDraftWorkflowStatus,
            name="letter_draft_workflow_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=LetterDraftWorkflowStatus.AI_DRAFT_CREATED,
    )
    issue_source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sections: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    validation: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    claim_warnings: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    send_guardrails: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    versions_history: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
