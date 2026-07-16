"""Per-organization dispute workflow settings."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, TimestampMixin
from api.database.base import Base

DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE = Decimal("1.00")
MIN_CROSS_BUREAU_BALANCE_TOLERANCE = Decimal("0.01")
MAX_CROSS_BUREAU_BALANCE_TOLERANCE = Decimal("100.00")


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
