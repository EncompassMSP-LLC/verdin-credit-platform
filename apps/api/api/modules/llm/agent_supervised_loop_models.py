"""Human-gated agent supervised loop run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class AgentSupervisedLoopStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class AgentSupervisedLoopRun(Base, TimestampMixin):
    __tablename__ = "agent_supervised_loop_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    tool_invocation_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_tool_invocation_requests.id"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    tool_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[AgentSupervisedLoopStatus] = mapped_column(
        Enum(
            AgentSupervisedLoopStatus,
            name="agent_supervised_loop_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    loop_summary: Mapped[str] = mapped_column(Text, nullable=False)
    steps_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
