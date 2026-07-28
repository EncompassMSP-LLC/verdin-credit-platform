"""Partner nurture drip models (LRP-206)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class NurtureAudience(StrEnum):
    LENDER = "lender"
    REALTOR = "realtor"
    PARTNER_LEAD = "partner_lead"


class NurtureLifecycleStage(StrEnum):
    LEAD = "lead"
    DISCOVERY = "discovery"
    ACTIVE = "active"
    NURTURE = "nurture"
    INACTIVE = "inactive"


class NurtureChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NurtureEnrollmentStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXITED = "exited"


class PartnerNurtureProgram(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "partner_nurture_programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    audience: Mapped[NurtureAudience] = mapped_column(
        Enum(
            NurtureAudience,
            name="partner_nurture_audience",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=NurtureAudience.LENDER,
    )
    enrollment_lifecycle_stage: Mapped[NurtureLifecycleStage] = mapped_column(
        Enum(
            NurtureLifecycleStage,
            name="partner_nurture_lifecycle_stage",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=NurtureLifecycleStage.LEAD,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class PartnerNurtureStep(Base, TimestampMixin):
    __tablename__ = "partner_nurture_steps"
    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "step_order",
            name="uq_partner_nurture_steps_program_order",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_nurture_programs.id"), nullable=False, index=True
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    delay_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    channel: Mapped[NurtureChannel] = mapped_column(
        Enum(
            NurtureChannel,
            name="partner_nurture_channel",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=NurtureChannel.EMAIL,
    )
    template_key: Mapped[str] = mapped_column(String(100), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)


class PartnerNurtureEnrollment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "partner_nurture_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_nurture_programs.id"), nullable=False, index=True
    )
    partnership_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("org_partnerships.id"), nullable=True, index=True
    )
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[NurtureEnrollmentStatus] = mapped_column(
        Enum(
            NurtureEnrollmentStatus,
            name="partner_nurture_enrollment_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=NurtureEnrollmentStatus.ACTIVE,
        index=True,
    )
    current_step_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tcpa_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class PartnerNurtureDeliveryRun(Base, TimestampMixin):
    """Idempotent per-enrollment step delivery audit."""

    __tablename__ = "partner_nurture_delivery_runs"
    __table_args__ = (
        UniqueConstraint(
            "enrollment_id",
            "step_id",
            name="uq_partner_nurture_delivery_enrollment_step",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_nurture_enrollments.id"), nullable=False, index=True
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_nurture_programs.id"), nullable=False
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_nurture_steps.id"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
