"""Persisted dispute response records (Phase 10).

Auditable record of a bureau/furnisher response to a sent dispute letter. Each
row is entered by staff (mail/portal/phone/email) — the platform never polls a
bureau. Layered over the simpler ``accounts.response_received`` flag so the
reinvestigation lifecycle keeps a full history per letter.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base

if TYPE_CHECKING:
    from api.modules.accounts.dispute_letter_models import DisputeLetter
    from api.modules.accounts.models import Account


class DisputeResponseOutcome(StrEnum):
    DELETED = "deleted"
    VERIFIED = "verified"
    UPDATED = "updated"
    CORRECTED = "corrected"
    NO_RESPONSE = "no_response"
    REJECTED = "rejected"


class DisputeResponseMethod(StrEnum):
    MAIL = "mail"
    PORTAL = "portal"
    PHONE = "phone"
    EMAIL = "email"
    OTHER = "other"


class DisputeResponse(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "dispute_responses"

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
    dispute_letter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dispute_letters.id"), nullable=True, index=True
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True
    )
    outcome: Mapped[DisputeResponseOutcome] = mapped_column(
        Enum(
            DisputeResponseOutcome,
            name="dispute_response_outcome",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    response_method: Mapped[DisputeResponseMethod] = mapped_column(
        Enum(
            DisputeResponseMethod,
            name="dispute_response_method",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=DisputeResponseMethod.MAIL,
    )
    response_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    account: Mapped[Account] = relationship()
    dispute_letter: Mapped[DisputeLetter | None] = relationship()
