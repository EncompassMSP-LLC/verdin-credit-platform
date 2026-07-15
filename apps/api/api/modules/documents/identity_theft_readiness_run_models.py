"""Persisted FCRA §605B submission-readiness audit runs (operator-gated).

Records the outcome of a staff-triggered readiness check for the §605B block
packet. This is an audit trail only — it never submits anything to a bureau.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class IdentityTheft605bReadinessRun(Base, TimestampMixin):
    __tablename__ = "identity_theft_605b_readiness_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    generated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    packet_readiness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confirmed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attestation_recorded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
