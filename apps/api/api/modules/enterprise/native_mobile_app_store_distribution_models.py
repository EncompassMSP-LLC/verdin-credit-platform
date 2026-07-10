"""Admin-gated native mobile app store distribution run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class NativeMobileAppStoreDistributionRunStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    READY = "ready"
    REJECTED = "rejected"
    FAILED = "failed"


class NativeMobileAppStoreDistributionRun(Base, TimestampMixin):
    __tablename__ = "native_mobile_app_store_distribution_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    native_mobile_passkey_client_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("native_mobile_passkey_client_runs.id"),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[NativeMobileAppStoreDistributionRunStatus] = mapped_column(
        Enum(
            NativeMobileAppStoreDistributionRunStatus,
            name="native_mobile_app_store_distribution_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    distribution_summary: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    store_target: Mapped[str] = mapped_column(String(50), nullable=False)
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
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
