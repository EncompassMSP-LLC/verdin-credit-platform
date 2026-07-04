"""Billing invoice collection run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class BillingInvoiceCollectionRunKind(StrEnum):
    INVOICE_PDF = "invoice_pdf"
    PAYMENT_REMINDER = "payment_reminder"


class BillingInvoiceCollectionTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class BillingInvoiceCollectionRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BillingInvoiceCollectionRun(Base, TimestampMixin):
    __tablename__ = "billing_invoice_collection_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    run_kind: Mapped[BillingInvoiceCollectionRunKind] = mapped_column(
        Enum(
            BillingInvoiceCollectionRunKind,
            name="billing_invoice_collection_run_kind",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    trigger_source: Mapped[BillingInvoiceCollectionTriggerSource] = mapped_column(
        Enum(
            BillingInvoiceCollectionTriggerSource,
            name="billing_invoice_collection_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[BillingInvoiceCollectionRunStatus] = mapped_column(
        Enum(
            BillingInvoiceCollectionRunStatus,
            name="billing_invoice_collection_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    invoices_pdf_generated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payment_reminders_queued: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    performed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
