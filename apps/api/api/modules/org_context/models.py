"""Per-organization feature flags for demo/training capabilities (LRP-109)."""

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class OrgDemoFeature(StrEnum):
    """Demo/training capabilities — never enabled implicitly for PRODUCTION orgs."""

    DEMO_DATA = "demo_data"
    DEMO_NOTIFICATIONS = "demo_notifications"
    SAMPLE_BORROWERS = "sample_borrowers"
    FAKE_CREDIT_REPORTS = "fake_credit_reports"
    TRAINING_MODE = "training_mode"


class OrganizationFeatureFlag(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "organization_feature_flags"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "feature",
            name="uq_organization_feature_flags_org_feature",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    feature: Mapped[OrgDemoFeature] = mapped_column(
        Enum(
            OrgDemoFeature,
            name="org_demo_feature",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
