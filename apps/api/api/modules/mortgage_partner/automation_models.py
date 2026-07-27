"""CRM automation rule persistence models (LRP-203)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class CrmAutomationTrigger(StrEnum):
    STAGE_ENTER = "stage_enter"
    REFERRAL_CREATED = "referral_created"
    TASK_OVERDUE = "task_overdue"
    SCORE_BAND_CHANGE = "score_band_change"
    DOCUMENT_UPLOADED = "document_uploaded"
    MANUAL = "manual"


class CrmAutomationChannel(StrEnum):
    TASK = "task"
    EMAIL = "email"
    SMS = "sms"
    NOTIFICATION = "notification"
    STAGE = "stage"


class CrmAutomationRule(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "crm_automation_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    trigger: Mapped[CrmAutomationTrigger] = mapped_column(
        Enum(
            CrmAutomationTrigger,
            name="crm_automation_trigger",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(500), nullable=False)
    channel: Mapped[CrmAutomationChannel] = mapped_column(
        Enum(
            CrmAutomationChannel,
            name="crm_automation_channel",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    last_fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fire_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
