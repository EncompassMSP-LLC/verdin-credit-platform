"""Weekly partner status digest models (LRP-207)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class PartnerWeeklyDigestSubscription(Base, TimestampMixin, SoftDeleteMixin):
    """Opt-in weekly digest delivery target for a partnership (LRP-207)."""

    __tablename__ = "partner_weekly_digest_subscriptions"
    __table_args__ = (
        UniqueConstraint(
            "partnership_id",
            "recipient_email",
            name="uq_partner_weekly_digest_sub_email",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    partnership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("org_partnerships.id"), nullable=False, index=True
    )
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # ISO weekday: 1=Monday … 7=Sunday (default Monday AM per §6 weekly report)
    send_weekday: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class PartnerWeeklyDigestRun(Base, TimestampMixin):
    """Idempotent per-partnership weekly digest archive (LRP-207)."""

    __tablename__ = "partner_weekly_digest_runs"
    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "week_key",
            name="uq_partner_weekly_digest_run_sub_week",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    partnership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("org_partnerships.id"), nullable=False, index=True
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partner_weekly_digest_subscriptions.id"),
        nullable=False,
        index=True,
    )
    week_key: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
