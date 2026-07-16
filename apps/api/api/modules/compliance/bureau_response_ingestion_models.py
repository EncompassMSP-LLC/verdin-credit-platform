"""Bureau response ingestion audit scaffold models (Phase 15).

Records operator-initiated scaffold runs for planned bureau response ingestion.
Live polling remains deferred — runs are stored with an explicit deferral reason.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class BureauResponseIngestionRunStatus(StrEnum):
    DEFERRED = "deferred"
    FAILED = "failed"


class BureauResponseIngestionRun(Base, TimestampMixin):
    __tablename__ = "bureau_response_ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    bureau_target: Mapped[str] = mapped_column(String(32), nullable=False, default="all")
    status: Mapped[BureauResponseIngestionRunStatus] = mapped_column(
        Enum(
            BureauResponseIngestionRunStatus,
            name="bureau_response_ingestion_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    deferral_reason: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
