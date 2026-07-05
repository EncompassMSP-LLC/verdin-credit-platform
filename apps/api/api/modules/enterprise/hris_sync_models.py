"""HRIS bidirectional sync run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class HrisBidirectionalSyncRunKind(StrEnum):
    EMPLOYEES_INBOUND = "employees_inbound"
    EMPLOYEES_OUTBOUND = "employees_outbound"


class HrisBidirectionalSyncTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class HrisBidirectionalSyncRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class HrisBidirectionalSyncRun(Base, TimestampMixin):
    __tablename__ = "hris_bidirectional_sync_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    run_kind: Mapped[HrisBidirectionalSyncRunKind] = mapped_column(
        Enum(
            HrisBidirectionalSyncRunKind,
            name="hris_bidirectional_sync_run_kind",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    trigger_source: Mapped[HrisBidirectionalSyncTriggerSource] = mapped_column(
        Enum(
            HrisBidirectionalSyncTriggerSource,
            name="hris_bidirectional_sync_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[HrisBidirectionalSyncRunStatus] = mapped_column(
        Enum(
            HrisBidirectionalSyncRunStatus,
            name="hris_bidirectional_sync_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    records_synced: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    performed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
