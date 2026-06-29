"""Documents domain models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class Document(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True
    )
    is_duplicate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    case: Mapped["Case"] = relationship(back_populates="documents")
    account: Mapped["Account | None"] = relationship()
    duplicate_of: Mapped["Document | None"] = relationship(remote_side=[id])
    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        order_by="DocumentVersion.version_number.desc()",
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    document: Mapped["Document"] = relationship(back_populates="versions")
