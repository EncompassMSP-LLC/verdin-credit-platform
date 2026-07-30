"""Staff-mediated document↔issue evidence vault associations (LRP-208A)."""

from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class IssueEvidenceLinkRole(StrEnum):
    SUPPORTING = "supporting"
    PRIMARY = "primary"
    IDENTITY = "identity"
    STATEMENT = "statement"


class IssueEvidenceLink(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Associates a case vault document with an explainability ``source_id``."""

    __tablename__ = "issue_evidence_links"
    __table_args__ = (
        Index(
            "uq_issue_evidence_links_case_source_doc_active",
            "case_id",
            "source_id",
            "document_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    source_id: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True
    )
    role: Mapped[IssueEvidenceLinkRole] = mapped_column(
        Enum(
            IssueEvidenceLinkRole,
            name="issue_evidence_link_role",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=IssueEvidenceLinkRole.SUPPORTING,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
