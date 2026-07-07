"""Admin-gated multi-IdP bulk provisioning run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class BulkIdpProvisioningRunStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    PROVISIONED = "provisioned"
    REJECTED = "rejected"
    FAILED = "failed"


class BulkIdpProvisioningRun(Base, TimestampMixin):
    __tablename__ = "bulk_idp_provisioning_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    hris_passwordless_ui_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hris_passwordless_ui_runs.id"),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[BulkIdpProvisioningRunStatus] = mapped_column(
        Enum(
            BulkIdpProvisioningRunStatus,
            name="bulk_idp_provisioning_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    provisioning_summary: Mapped[str] = mapped_column(Text, nullable=False)
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
    provisioned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
