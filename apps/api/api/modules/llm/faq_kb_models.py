"""FAQ/KB retrieval conversation audit models (LRP-405)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class FaqKbAudience(StrEnum):
    BORROWER = "borrower"
    LENDER = "lender"
    REALTOR = "realtor"
    STAFF = "staff"


class FaqKbFeedbackRating(StrEnum):
    ACCURATE = "accurate"
    INACCURATE = "inaccurate"
    INCOMPLETE = "incomplete"


class FaqKbConversationTurn(Base, TimestampMixin):
    __tablename__ = "faq_kb_conversation_turns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    audience: Mapped[FaqKbAudience] = mapped_column(
        Enum(
            FaqKbAudience,
            name="faq_kb_audience",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    grounded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    refused: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    refusal_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    matched_article_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_rating: Mapped[FaqKbFeedbackRating | None] = mapped_column(
        Enum(
            FaqKbFeedbackRating,
            name="faq_kb_feedback_rating",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=True,
    )
    feedback_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    feedback_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
