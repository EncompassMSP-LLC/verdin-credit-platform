"""Billing invoicing and dunning run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class BillingInvoicingRunKind(StrEnum):
    INVOICE_CYCLE = "invoice_cycle"
    DUNNING_REMINDER = "dunning_reminder"


class BillingInvoicingTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class BillingInvoicingRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BillingInvoicingRun(Base, TimestampMixin):
    __tablename__ = "billing_invoicing_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    run_kind: Mapped[BillingInvoicingRunKind] = mapped_column(
        Enum(
            BillingInvoicingRunKind,
            name="billing_invoicing_run_kind",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    trigger_source: Mapped[BillingInvoicingTriggerSource] = mapped_column(
        Enum(
            BillingInvoicingTriggerSource,
            name="billing_invoicing_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[BillingInvoicingRunStatus] = mapped_column(
        Enum(
            BillingInvoicingRunStatus,
            name="billing_invoicing_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    invoices_prepared: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dunning_reminders_queued: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    performed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
