"""Per-organization dispute workflow settings."""

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, TimestampMixin
from api.database.base import Base

DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE = Decimal("1.00")
MIN_CROSS_BUREAU_BALANCE_TOLERANCE = Decimal("0.01")
MAX_CROSS_BUREAU_BALANCE_TOLERANCE = Decimal("100.00")

DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS = 90
DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS = 30
MIN_REINVESTIGATION_BENCHMARK_BASELINE_DAYS = 7
MAX_REINVESTIGATION_BENCHMARK_BASELINE_DAYS = 365
MIN_REINVESTIGATION_BENCHMARK_RECENT_DAYS = 1

BENCHMARK_WINDOW_BUREAUS = frozenset({"equifax", "experian", "transunion"})


class OrganizationDisputeSettings(Base, TimestampMixin, AuditMixin):
    """Org-scoped dispute comparison and reinvestigation configuration."""

    __tablename__ = "organization_dispute_settings"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_organization_dispute_settings_org"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    cross_bureau_balance_tolerance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE,
    )
    reinvestigation_benchmark_baseline_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
    )
    reinvestigation_benchmark_recent_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
    )
    reinvestigation_benchmark_bureau_windows: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
