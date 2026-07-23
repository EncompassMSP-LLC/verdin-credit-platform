"""Persisted Lending Readiness / credit-analysis runs (Vol 22)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class CreditAnalysisRun(Base, TimestampMixin):
    __tablename__ = "credit_analysis_runs"

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
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="published", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    score_version: Mapped[str] = mapped_column(String(32), nullable=False)
    formula_version: Mapped[str] = mapped_column(String(32), nullable=False)
    inputs_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    reports_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tradelines_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    borrower_readiness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    mortgage_readiness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    band: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
