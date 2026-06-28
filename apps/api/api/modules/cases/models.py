"""Cases domain models."""

import uuid
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class CaseStatus(StrEnum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Case(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CaseStatus.OPEN,
    )
    case_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="cases")
    account: Mapped["Account | None"] = relationship(back_populates="cases")
    assigned_to: Mapped["User | None"] = relationship(
        back_populates="assigned_cases", foreign_keys=[assigned_to_id]
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="case")
    tasks: Mapped[list["Task"]] = relationship(back_populates="case")
    communications: Mapped[list["Communication"]] = relationship(back_populates="case")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="case")
