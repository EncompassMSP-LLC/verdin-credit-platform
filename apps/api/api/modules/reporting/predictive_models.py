"""ORM models for predictive outcome snapshots and refresh audit."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class PredictiveOutcomeTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class PredictiveOutcomeRefreshStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class PredictiveOutcomeSnapshot(Base, TimestampMixin):
    __tablename__ = "predictive_outcome_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    refreshed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PredictiveOutcomeRefreshRun(Base, TimestampMixin):
    __tablename__ = "predictive_outcome_refresh_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    trigger_source: Mapped[PredictiveOutcomeTriggerSource] = mapped_column(
        Enum(
            PredictiveOutcomeTriggerSource,
            name="predictive_outcome_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[PredictiveOutcomeRefreshStatus] = mapped_column(
        Enum(
            PredictiveOutcomeRefreshStatus,
            name="predictive_outcome_refresh_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
