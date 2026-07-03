"""ORM models for reporting materialized view refresh audit."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class ReportingMvTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class ReportingMvRefreshStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class ReportingMvRefreshRun(Base, TimestampMixin):
    __tablename__ = "reporting_mv_refresh_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )
    trigger_source: Mapped[ReportingMvTriggerSource] = mapped_column(
        Enum(
            ReportingMvTriggerSource,
            name="reporting_mv_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[ReportingMvRefreshStatus] = mapped_column(
        Enum(
            ReportingMvRefreshStatus,
            name="reporting_mv_refresh_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    views_refreshed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
