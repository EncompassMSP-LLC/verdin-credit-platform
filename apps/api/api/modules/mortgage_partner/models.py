"""Mortgage Partner Edition — partnership, membership, referral, and access audit models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class PartnerOrgType(StrEnum):
    LENDER = "lender"
    REALTOR = "realtor"
    BROKER = "broker"
    OPERATOR = "operator"
    OTHER = "other"


class PartnershipStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class PartnerRole(StrEnum):
    """Partnership-scoped roles (edition overlay — not staff UserRole)."""

    LENDER_ADMIN = "lender_admin"
    LOAN_OFFICER = "loan_officer"
    CREDIT_OPS = "credit_ops"
    UNDERWRITER_VIEW = "underwriter_view"
    READ_ONLY = "read_only"


class ReferralStatus(StrEnum):
    NEW = "new"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


class PartnerAccessAction(StrEnum):
    PARTNERSHIP_VIEW = "partnership_view"
    REFERRAL_LIST = "referral_list"
    REFERRAL_VIEW = "referral_view"
    MEMBER_LIST = "member_list"
    MEMBER_CREATE = "member_create"
    PARTNERSHIP_CREATE = "partnership_create"
    REFERRAL_CREATE = "referral_create"
    REFERRAL_UPDATE = "referral_update"


class OrgPartnership(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """CRO organization ↔ partner organization link (Lender / Realtor / etc.)."""

    __tablename__ = "org_partnerships"
    __table_args__ = (
        UniqueConstraint(
            "cro_organization_id",
            "partner_organization_id",
            name="uq_org_partnerships_cro_partner",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cro_organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    partner_organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    partner_type: Mapped[PartnerOrgType] = mapped_column(
        Enum(
            PartnerOrgType,
            name="partner_org_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=PartnerOrgType.LENDER,
    )
    status: Mapped[PartnershipStatus] = mapped_column(
        Enum(
            PartnershipStatus,
            name="partnership_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=PartnershipStatus.PENDING,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class OrgPartnershipMember(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """User membership on a partnership with a partner-scoped role."""

    __tablename__ = "org_partnership_members"
    __table_args__ = (
        UniqueConstraint(
            "partnership_id",
            "user_id",
            name="uq_org_partnership_members_partnership_user",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("org_partnerships.id"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
        comment="CRO org that owns the partnership (tenant scope)",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    partner_role: Mapped[PartnerRole] = mapped_column(
        Enum(
            PartnerRole,
            name="partner_role",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=PartnerRole.READ_ONLY,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class PartnerReferral(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Applicant referral attributed to a CRO↔partner partnership."""

    __tablename__ = "partner_referrals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("org_partnerships.id"),
        nullable=False,
        index=True,
    )
    cro_organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=True,
        index=True,
    )
    status: Mapped[ReferralStatus] = mapped_column(
        Enum(
            ReferralStatus,
            name="partner_referral_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ReferralStatus.NEW,
        index=True,
    )
    source_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    referred_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )


class PartnerAccessAudit(Base, TimestampMixin):
    """Audit of partner-scoped access and mutations (SOC2 / access evidence)."""

    __tablename__ = "partner_access_audits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cro_organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    partnership_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("org_partnerships.id"),
        nullable=True,
        index=True,
    )
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    action: Mapped[PartnerAccessAction] = mapped_column(
        Enum(
            PartnerAccessAction,
            name="partner_access_action",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
