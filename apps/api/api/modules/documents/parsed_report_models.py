"""Persisted structured credit report parser output."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import TimestampMixin
from api.database.base import Base

if TYPE_CHECKING:
    from api.modules.documents.models import Document


class DocumentParsedCreditReport(Base, TimestampMixin):
    __tablename__ = "document_parsed_credit_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    bureau: Mapped[str] = mapped_column(String(50), nullable=False)
    parser_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    parser_confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    parsed_report: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    is_partial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    warnings: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    document: Mapped[Document] = relationship(back_populates="parsed_credit_report")
