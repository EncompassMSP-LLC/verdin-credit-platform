"""Persisted Identity Theft Case Center entities (Phase 8)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class IdentityTheftIncidentStatus(StrEnum):
    OPEN = "open"
    IN_RECOVERY = "in_recovery"
    CLOSED = "closed"


class IdentityTheftConfirmation(StrEnum):
    RECOGNIZE = "recognize"
    NEED_MORE_INFO = "need_more_info"
    INACCURATE_REPORTING = "inaccurate_reporting"
    IDENTITY_THEFT = "identity_theft"
    MIXED_FILE = "mixed_file"
    AUTHORIZED_USER = "authorized_user"
    UNSURE = "unsure"


class IdentityTheftIssueType(StrEnum):
    IDENTITY_THEFT_INDICATOR = "IDENTITY_THEFT_INDICATOR"
    CONFIRMED_IDENTITY_THEFT_CLAIM = "CONFIRMED_IDENTITY_THEFT_CLAIM"


class IdentityTheftProtectionType(StrEnum):
    INITIAL_FRAUD_ALERT = "initial_fraud_alert"
    EXTENDED_FRAUD_ALERT = "extended_fraud_alert"
    ACTIVE_DUTY_ALERT = "active_duty_alert"
    EQUIFAX_FREEZE = "equifax_freeze"
    EXPERIAN_FREEZE = "experian_freeze"
    TRANSUNION_FREEZE = "transunion_freeze"


class IdentityTheftProtectionStatusValue(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    UNFROZEN = "unfrozen"
    UNKNOWN = "unknown"


class IdentityTheftIncident(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Case-scoped identity-theft recovery workflow (opened only after confirmation)."""

    __tablename__ = "identity_theft_incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    status: Mapped[IdentityTheftIncidentStatus] = mapped_column(
        Enum(
            IdentityTheftIncidentStatus,
            name="identity_theft_incident_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=IdentityTheftIncidentStatus.OPEN,
    )
    discovered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    suspected_theft_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    suspected_theft_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    unrecognized_addresses: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    unrecognized_aliases: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    companies_contacted: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    police_report_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    police_report_agency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    police_report_filed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    ftc_report_status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="not_started"
    )
    ftc_report_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_checklist: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    recovery_step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    consumer_attestation_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consumer_attestation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class IdentityTheftAccountReview(Base, TimestampMixin, AuditMixin):
    """Per-tradeline consumer confirmation gate for identity-theft indicators."""

    __tablename__ = "identity_theft_account_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identity_theft_incidents.id"),
        nullable=True,
        index=True,
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True, index=True
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True
    )
    bureau: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tradeline_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    match_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    creditor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_number_masked: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detection_source: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    issue_type: Mapped[IdentityTheftIssueType] = mapped_column(
        Enum(
            IdentityTheftIssueType,
            name="identity_theft_issue_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=IdentityTheftIssueType.IDENTITY_THEFT_INDICATOR,
    )
    consumer_confirmation: Mapped[IdentityTheftConfirmation | None] = mapped_column(
        Enum(
            IdentityTheftConfirmation,
            name="identity_theft_confirmation",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=True,
    )
    consumer_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ordinary_dispute_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    legal_path: Mapped[str | None] = mapped_column(String(64), nullable=True)
    packet_readiness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    missing_evidence: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    attestation_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class IdentityTheftProtection(Base, TimestampMixin, AuditMixin):
    """Fraud-alert and bureau freeze tracking for a case."""

    __tablename__ = "identity_theft_protections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True
    )
    protection_type: Mapped[IdentityTheftProtectionType] = mapped_column(
        Enum(
            IdentityTheftProtectionType,
            name="identity_theft_protection_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    status: Mapped[IdentityTheftProtectionStatusValue] = mapped_column(
        Enum(
            IdentityTheftProtectionStatusValue,
            name="identity_theft_protection_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=IdentityTheftProtectionStatusValue.UNKNOWN,
    )
    placed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="staff_recorded")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
