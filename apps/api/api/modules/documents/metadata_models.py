"""Document metadata and entity resolution models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import TimestampMixin
from api.database.base import Base

if TYPE_CHECKING:
    from api.modules.documents.models import Document


class DocumentMetadata(Base, TimestampMixin):
    __tablename__ = "document_metadata"

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
    consumer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bureau: Mapped[str | None] = mapped_column(String(50), nullable=True)
    creditor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    collection_agency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_number_masked: Mapped[str | None] = mapped_column(String(50), nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    open_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    balance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    addresses: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    phone_numbers: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    ssn_masked: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(20), nullable=False, default="rules")
    metadata_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extraction_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped[Document] = relationship(back_populates="metadata")

    def as_resolution_metadata(self) -> dict[str, str | float | list[str] | None]:
        return {
            "consumer_name": self.consumer_name,
            "bureau": self.bureau,
            "creditor": self.creditor,
            "collection_agency": self.collection_agency,
            "account_number_masked": self.account_number_masked,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "open_date": self.open_date.isoformat() if self.open_date else None,
            "balance": float(self.balance) if self.balance is not None else None,
            "payment_status": self.payment_status,
            "addresses": list(self.addresses or []),
            "phone_numbers": list(self.phone_numbers or []),
            "ssn_masked": self.ssn_masked,
        }


class DocumentEntityResolution(Base, TimestampMixin):
    __tablename__ = "document_entity_resolutions"
    __table_args__ = (
        UniqueConstraint("document_id", "entity_type", name="uq_document_entity_resolution_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    matched_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    resolution_method: Mapped[str] = mapped_column(String(20), nullable=False, default="rules")
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_entity_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    document: Mapped[Document] = relationship(back_populates="entity_resolutions")
