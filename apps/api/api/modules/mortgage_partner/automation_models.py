"""CRM automation rule persistence models (LRP-203) + audit events (LRP-502)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
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


class CrmAutomationAuditEventKind(StrEnum):
    RULE_CREATED = "rule_created"
    RULE_UPDATED = "rule_updated"
    RULE_ENABLED = "rule_enabled"
    RULE_DISABLED = "rule_disabled"
    RULE_FIRED = "rule_fired"
    RULE_DRY_RUN = "rule_dry_run"
    RULE_SKIPPED = "rule_skipped"


class CrmAutomationAuditStatus(StrEnum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    DRY_RUN = "dry_run"


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


class CrmAutomationAuditEvent(Base):
    """Durable CRM automation config + fire audit (LRP-502)."""

    __tablename__ = "crm_automation_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm_automation_rules.id"), nullable=True, index=True
    )
    event_kind: Mapped[CrmAutomationAuditEventKind] = mapped_column(
        Enum(
            CrmAutomationAuditEventKind,
            name="crm_automation_audit_event_kind",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    trigger: Mapped[str | None] = mapped_column(String(64), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[CrmAutomationAuditStatus] = mapped_column(
        Enum(
            CrmAutomationAuditStatus,
            name="crm_automation_audit_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    schema_version: Mapped[str] = mapped_column(
        String(32), nullable=False, default="crm-automation-audit-v1"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
