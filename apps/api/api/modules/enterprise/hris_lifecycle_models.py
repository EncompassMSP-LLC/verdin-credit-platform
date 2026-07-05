"""Admin-gated HRIS lifecycle sync run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base
from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunKind


class HrisLifecycleSyncRunStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class HrisLifecycleSyncRun(Base, TimestampMixin):
    __tablename__ = "hris_lifecycle_sync_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    hris_bidirectional_sync_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hris_bidirectional_sync_runs.id"),
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
    status: Mapped[HrisLifecycleSyncRunStatus] = mapped_column(
        Enum(
            HrisLifecycleSyncRunStatus,
            name="hris_lifecycle_sync_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    lifecycle_summary: Mapped[str] = mapped_column(Text, nullable=False)
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
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
