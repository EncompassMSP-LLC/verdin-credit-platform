"""CRM appointments + reminder audit models (LRP-205)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class CrmAppointmentStatus(StrEnum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class CrmAppointmentType(StrEnum):
    CONSULTATION = "consultation"
    CALL = "call"
    MEETING = "meeting"
    FOLLOW_UP = "follow_up"
    REVIEW = "review"


class AppointmentReminderOffset(StrEnum):
    T24H = "t24h"
    T1H = "t1h"


class CrmAppointment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "crm_appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    appointment_type: Mapped[CrmAppointmentType] = mapped_column(
        Enum(
            CrmAppointmentType,
            name="crm_appointment_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=CrmAppointmentType.CONSULTATION,
    )
    status: Mapped[CrmAppointmentStatus] = mapped_column(
        Enum(
            CrmAppointmentStatus,
            name="crm_appointment_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=CrmAppointmentStatus.SCHEDULED,
        index=True,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    related_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    borrower_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    borrower_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    borrower_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    referring_lo_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    referring_lo_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tcpa_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class AppointmentReminderRun(Base, TimestampMixin):
    """Idempotent reminder fan-out audit (T-24h / T-1h)."""

    __tablename__ = "appointment_reminder_runs"
    __table_args__ = (
        UniqueConstraint(
            "appointment_id",
            "offset_key",
            name="uq_appointment_reminder_runs_appointment_offset",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    appointment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm_appointments.id"), nullable=False, index=True
    )
    offset_key: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    matrix_dispatch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notification_matrix_dispatches.id"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
