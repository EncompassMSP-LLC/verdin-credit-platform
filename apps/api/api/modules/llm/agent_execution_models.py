"""Human-gated agent execution step models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base
from api.modules.llm.agent_observability_models import AgentObservabilityKind


class AgentExecutionStepStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    EXECUTED = "executed"
    REJECTED = "rejected"
    FAILED = "failed"


class AgentExecutionStep(Base, TimestampMixin):
    __tablename__ = "agent_execution_steps"

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
    status: Mapped[AgentExecutionStepStatus] = mapped_column(
        Enum(
            AgentExecutionStepStatus,
            name="agent_execution_step_status",
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
    step_summary: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    timeline_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("timeline_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
