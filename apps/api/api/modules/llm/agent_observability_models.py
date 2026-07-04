"""Agent observability run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class AgentObservabilityKind(StrEnum):
    CASE_REVIEW = "case_review"
    DOCUMENT_TRIAGE = "document_triage"
    DISPUTE_PREP = "dispute_prep"


class AgentObservabilityTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class AgentObservabilityRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentObservabilityRun(Base, TimestampMixin):
    __tablename__ = "agent_observability_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    agent_kind: Mapped[AgentObservabilityKind] = mapped_column(
        Enum(
            AgentObservabilityKind,
            name="agent_observability_kind",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    trigger_source: Mapped[AgentObservabilityTriggerSource] = mapped_column(
        Enum(
            AgentObservabilityTriggerSource,
            name="agent_observability_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[AgentObservabilityRunStatus] = mapped_column(
        Enum(
            AgentObservabilityRunStatus,
            name="agent_observability_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    steps_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    steps_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    timeline_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("timeline_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    performed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
