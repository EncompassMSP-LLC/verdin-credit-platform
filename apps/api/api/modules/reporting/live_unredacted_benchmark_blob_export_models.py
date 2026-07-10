"""Admin-gated live unredacted benchmark blob export run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class LiveUnredactedBenchmarkBlobExportRunStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    EXPORTED = "exported"
    REJECTED = "rejected"
    FAILED = "failed"


class LiveUnredactedBenchmarkBlobExportRun(Base, TimestampMixin):
    __tablename__ = "live_unredacted_benchmark_blob_export_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    unredacted_export_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("unredacted_cross_org_benchmark_export_runs.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[LiveUnredactedBenchmarkBlobExportRunStatus] = mapped_column(
        Enum(
            LiveUnredactedBenchmarkBlobExportRunStatus,
            name="live_unredacted_benchmark_blob_export_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    export_summary: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
