"""SMS marketing campaign run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class SmsMarketingTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class SmsMarketingCampaignStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SmsMarketingCampaignRun(Base, TimestampMixin):
    __tablename__ = "sms_marketing_campaign_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    campaign_name: Mapped[str] = mapped_column(String(120), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_user_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    trigger_source: Mapped[SmsMarketingTriggerSource] = mapped_column(
        Enum(
            SmsMarketingTriggerSource,
            name="sms_marketing_trigger_source",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[SmsMarketingCampaignStatus] = mapped_column(
        Enum(
            SmsMarketingCampaignStatus,
            name="sms_marketing_campaign_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    recipients_queued: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    messages_sent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    messages_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    performed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
