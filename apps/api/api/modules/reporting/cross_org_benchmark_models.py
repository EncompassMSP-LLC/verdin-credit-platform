"""Cross-org benchmark analytics run models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.database.base import Base, TimestampMixin


class CrossOrgBenchmarkTriggerSource(enum.StrEnum):
    MANUAL = "manual"


class CrossOrgBenchmarkRunStatus(enum.StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class CrossOrgBenchmarkRun(Base, TimestampMixin):
    __tablename__ = "cross_org_benchmark_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requested_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trigger_source: Mapped[CrossOrgBenchmarkTriggerSource] = mapped_column(
        Enum(
            CrossOrgBenchmarkTriggerSource,
            name="cross_org_benchmark_trigger_source",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=CrossOrgBenchmarkTriggerSource.MANUAL,
    )
    status: Mapped[CrossOrgBenchmarkRunStatus] = mapped_column(
        Enum(
            CrossOrgBenchmarkRunStatus,
            name="cross_org_benchmark_run_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=CrossOrgBenchmarkRunStatus.COMPLETED,
    )
    organizations_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
