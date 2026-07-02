"""Cases domain models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class CaseStatus(StrEnum):
    OPEN = "open"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CaseStage(StrEnum):
    INTAKE = "intake"
    REVIEW = "review"
    EVIDENCE_GATHERING = "evidence_gathering"
    DISPUTE_PREPARATION = "dispute_preparation"
    AWAITING_RESPONSE = "awaiting_response"
    MONITORING = "monitoring"
    COMPLETE = "complete"


class CasePriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Case(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    case_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True
    )
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CaseStatus.OPEN,
        index=True,
    )
    stage: Mapped[CaseStage] = mapped_column(
        Enum(CaseStage, name="case_stage", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CaseStage.INTAKE,
        index=True,
    )
    priority: Mapped[CasePriority] = mapped_column(
        Enum(CasePriority, name="case_priority", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CasePriority.MEDIUM,
        index=True,
    )
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    client: Mapped["Client | None"] = relationship(back_populates="cases")
    organization: Mapped["Organization"] = relationship(back_populates="cases")
    assigned_to: Mapped["User | None"] = relationship(
        back_populates="assigned_cases", foreign_keys=[assigned_to_id]
    )
    credit_accounts: Mapped[list["Account"]] = relationship(back_populates="case")
    documents: Mapped[list["Document"]] = relationship(back_populates="case")
    tasks: Mapped[list["Task"]] = relationship(back_populates="case")
    communications: Mapped[list["Communication"]] = relationship(back_populates="case")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="case")
