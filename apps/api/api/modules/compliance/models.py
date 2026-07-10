"""Compliance center domain models — consent history and retention placeholders."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class ConsentType(StrEnum):
    CROA_SERVICES = "croa_services"
    FCRA_DISPUTE = "fcra_dispute"
    FDCPA_CONTACT = "fdcpa_contact"
    MARKETING = "marketing"
    DATA_PROCESSING = "data_processing"


class ConsentStatus(StrEnum):
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"


class ConsentSignatureMethod(StrEnum):
    STAFF_UPLOAD = "staff_upload"
    PORTAL_ATTESTATION = "portal_attestation"
    PORTAL_SIGNATURE_IMAGE = "portal_signature_image"
    PORTAL_GENERATED_DOCUMENT = "portal_generated_document"


class ConsentTemplateReviewStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"


class RetentionScope(StrEnum):
    DOCUMENTS = "documents"
    COMMUNICATIONS = "communications"
    AUDIT_LOGS = "audit_logs"
    CLIENT_PROFILES = "client_profiles"


class ConsentRecord(Base, TimestampMixin, AuditMixin):
    __tablename__ = "consent_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True, index=True
    )
    consent_type: Mapped[ConsentType] = mapped_column(
        Enum(ConsentType, name="consent_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus, name="consent_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ConsentStatus.GRANTED,
        index=True,
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="staff")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True
    )
    signature_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    document_template_key: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)


class ConsentDocumentTemplate(Base, TimestampMixin, AuditMixin):
    __tablename__ = "consent_document_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    template_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    merge_field_defaults: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    legal_review_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ConsentTemplateReviewStatus.DRAFT.value
    )


class RetentionPolicy(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "retention_policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[RetentionScope] = mapped_column(
        Enum(
            RetentionScope, name="retention_scope", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        index=True,
    )
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class EnforcementTriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class EnforcementRunStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RetentionEnforcementRun(Base, TimestampMixin):
    __tablename__ = "retention_enforcement_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("retention_policies.id"), nullable=True, index=True
    )
    scope: Mapped[RetentionScope | None] = mapped_column(
        Enum(
            RetentionScope,
            name="retention_scope",
            values_callable=lambda x: [e.value for e in x],
            create_constraint=False,
        ),
        nullable=True,
    )
    trigger_source: Mapped[EnforcementTriggerSource] = mapped_column(
        Enum(
            EnforcementTriggerSource,
            name="enforcement_trigger_source",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    status: Mapped[EnforcementRunStatus] = mapped_column(
        Enum(
            EnforcementRunStatus,
            name="enforcement_run_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    items_scanned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_enforced: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
