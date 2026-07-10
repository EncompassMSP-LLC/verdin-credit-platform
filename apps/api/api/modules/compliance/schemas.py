"""Compliance center domain schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.compliance.consent_signature import is_consent_signed
from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey
from api.modules.compliance.models import (
    ConsentRecord,
    ConsentStatus,
    ConsentType,
    EnforcementRunStatus,
    EnforcementTriggerSource,
    RetentionEnforcementRun,
    RetentionPolicy,
    RetentionScope,
)

ConsentSortField = Literal["granted_at", "created_at", "consent_type", "status"]
ConsentSortOrder = Literal["asc", "desc"]

RetentionSortField = Literal["created_at", "name", "scope", "retention_days"]
RetentionSortOrder = Literal["asc", "desc"]


class ConsentRecordCreate(BaseSchema):
    client_id: uuid.UUID
    case_id: uuid.UUID | None = None
    consent_type: ConsentType
    source: str = Field(default="staff", min_length=1, max_length=50)
    notes: str | None = None
    granted_at: datetime | None = None


class ConsentRecordListParams(PaginationParams):
    client_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None
    consent_type: ConsentType | None = None
    status: ConsentStatus | None = None
    sort_by: ConsentSortField = "granted_at"
    sort_order: ConsentSortOrder = "desc"


class ConsentRecordResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    case_id: uuid.UUID | None
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: datetime
    withdrawn_at: datetime | None
    source: str
    notes: str | None
    document_id: uuid.UUID | None
    signature_method: str | None
    signed_at: datetime | None
    signer_name: str | None
    document_template_key: str | None
    is_signed: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, record: ConsentRecord) -> "ConsentRecordResponse":
        return cls(
            id=record.id,
            organization_id=record.organization_id,
            client_id=record.client_id,
            case_id=record.case_id,
            consent_type=record.consent_type,
            status=record.status,
            granted_at=record.granted_at,
            withdrawn_at=record.withdrawn_at,
            source=record.source,
            notes=record.notes,
            document_id=record.document_id,
            signature_method=record.signature_method,
            signed_at=record.signed_at,
            signer_name=record.signer_name,
            document_template_key=record.document_template_key,
            is_signed=is_consent_signed(record),
            created_at=record.created_at,
            updated_at=record.updated_at,
            created_by_id=record.created_by_id,
            updated_by_id=record.updated_by_id,
        )


class ConsentUploadCreate(BaseSchema):
    client_id: uuid.UUID
    case_id: uuid.UUID
    consent_type: ConsentType
    signer_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class PortalConsentSignCreate(BaseSchema):
    template_key: ConsentDocumentTemplateKey
    signer_name: str = Field(min_length=1, max_length=255)
    attestation_accepted: bool


class PortalConsentRequirementResponse(BaseSchema):
    template_key: ConsentDocumentTemplateKey
    consent_type: ConsentType
    label: str
    title: str
    is_signed: bool
    consent_id: uuid.UUID | None
    legal_review_status: str


class PortalCaseConsentsResponse(BaseSchema):
    items: list[PortalConsentRequirementResponse]
    legal_review_notice: str


class ConsentDocumentTemplateResponse(BaseSchema):
    template_key: ConsentDocumentTemplateKey
    title: str
    body_text: str
    merge_field_defaults: dict[str, str] | None
    legal_review_status: str
    is_customized: bool
    updated_at: datetime | None


class ConsentDocumentTemplateUpdate(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    body_text: str = Field(min_length=1)
    merge_field_defaults: dict[str, str] | None = None
    legal_review_status: str = Field(default="draft", max_length=20)


class ConsentTemplatePreviewParams(BaseSchema):
    client_id: uuid.UUID
    case_id: uuid.UUID | None = None


class ClientConsentGapsResponse(BaseSchema):
    missing_template_keys: list[str]
    missing_template_labels: list[str]
    missing_consent_types: list[str]


class RetentionPolicyCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    scope: RetentionScope
    retention_days: int = Field(ge=1, le=36500)
    is_active: bool = True
    description: str | None = None


class RetentionPolicyUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    retention_days: int | None = Field(default=None, ge=1, le=36500)
    is_active: bool | None = None
    description: str | None = None


class RetentionPolicyListParams(PaginationParams):
    scope: RetentionScope | None = None
    is_active: bool | None = None
    sort_by: RetentionSortField = "created_at"
    sort_order: RetentionSortOrder = "desc"


class RetentionPolicyResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    scope: RetentionScope
    retention_days: int
    is_active: bool
    description: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, policy: RetentionPolicy) -> "RetentionPolicyResponse":
        return cls(
            id=policy.id,
            organization_id=policy.organization_id,
            name=policy.name,
            scope=policy.scope,
            retention_days=policy.retention_days,
            is_active=policy.is_active,
            description=policy.description,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
            deleted_at=policy.deleted_at,
            created_by_id=policy.created_by_id,
            updated_by_id=policy.updated_by_id,
        )


class ComplianceCenterStatusResponse(BaseSchema):
    consent_records_enabled: bool
    retention_policies_enabled: bool
    consent_type_count: int
    retention_scope_count: int
    capabilities: list[str]
    deferred_capabilities: list[str]


class RetentionEnforcementStatusResponse(BaseSchema):
    enabled: bool
    active_policy_count: int
    last_run_at: datetime | None


class RetentionEnforcementRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    policy_id: uuid.UUID | None
    scope: RetentionScope | None
    trigger_source: EnforcementTriggerSource
    status: EnforcementRunStatus
    items_scanned: int
    items_enforced: int
    started_at: datetime
    completed_at: datetime
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, run: RetentionEnforcementRun) -> "RetentionEnforcementRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            policy_id=run.policy_id,
            scope=run.scope,
            trigger_source=run.trigger_source,
            status=run.status,
            items_scanned=run.items_scanned,
            items_enforced=run.items_enforced,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )


class RetentionEnforcementRunListParams(PaginationParams):
    pass


class RetentionEnforcementRunResultResponse(BaseSchema):
    policies_processed: int
    items_enforced: int
    runs: list[RetentionEnforcementRunResponse]
