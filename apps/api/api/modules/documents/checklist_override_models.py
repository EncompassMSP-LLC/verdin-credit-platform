"""Dispute strategy checklist staff override model."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class DisputeStrategyChecklistOverride(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "dispute_strategy_checklist_overrides"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "case_id",
            "checklist_kind",
            "account_key",
            "item_id",
            name="uq_dispute_strategy_checklist_override_key",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    checklist_kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    account_key: Mapped[str] = mapped_column(String(255), nullable=False)
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    completion_status: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
