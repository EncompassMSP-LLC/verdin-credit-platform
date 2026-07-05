"""LLM dispute draft augment audit models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class LlmDisputeDraftAugmentStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class LlmDisputeDraftAugment(Base, TimestampMixin):
    __tablename__ = "llm_dispute_draft_augments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
    )
    recipient_type: Mapped[str] = mapped_column(String(50), nullable=False)
    base_template_id: Mapped[str] = mapped_column(String(100), nullable=False)
    base_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    base_body: Mapped[str] = mapped_column(Text, nullable=False)
    augmented_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LlmDisputeDraftAugmentStatus] = mapped_column(
        Enum(
            LlmDisputeDraftAugmentStatus,
            name="llm_dispute_draft_augment_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
