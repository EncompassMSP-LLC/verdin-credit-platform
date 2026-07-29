"""Pydantic schemas for Intelligent Letter Draft Builder (LRP-406)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.accounts.letter_draft_builder_models import LetterDraftWorkflowStatus

LetterTemplateKindLiteral = Literal[
    "bureau_dispute",
    "furnisher_dispute",
    "method_of_verification",
    "cfpb_complaint",
    "ftc_identity_theft",
    "debt_validation",
    "goodwill",
    "late_payment_forgiveness",
    "pay_for_delete",
    "communication_preference",
    "cease_communication",
    "mortgage_explanation",
    "custom_staff",
]

FactClassificationLiteral = Literal[
    "verified",
    "client_statement",
    "document_supported",
    "staff_observation",
]


class LetterDraftSection(BaseSchema):
    key: str
    heading: str
    body: str
    fact_classification: FactClassificationLiteral
    evidence_refs: list[dict[str, Any]] = Field(default_factory=list)
    editable: bool = True


class LetterDraftCreateRequest(BaseSchema):
    template_kind: LetterTemplateKindLiteral
    issue_source_id: str | None = Field(default=None, max_length=128)
    account_id: uuid.UUID | None = None


class LetterDraftSectionUpdateRequest(BaseSchema):
    body: str | None = None
    fact_classification: FactClassificationLiteral | None = None


class LetterDraftAdvanceRequest(BaseSchema):
    target_status: LetterDraftWorkflowStatus


class LetterDraftMarkSentRequest(BaseSchema):
    """Explicit staff record that a draft was transmitted outside the platform."""

    note: str | None = Field(default=None, max_length=500)


class LetterDraftTemplateSummary(BaseSchema):
    kind: LetterTemplateKindLiteral
    title: str
    description: str
    claim_warnings: list[str]


class LetterDraftResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID
    created_by_user_id: uuid.UUID | None
    template_kind: LetterTemplateKindLiteral
    template_title: str | None = None
    workflow_status: LetterDraftWorkflowStatus
    issue_source_id: str | None
    account_id: uuid.UUID | None
    version: int
    sections: list[LetterDraftSection]
    full_text: str
    validation: dict[str, Any]
    claim_warnings: list[str]
    send_guardrails: dict[str, Any]
    versions_history: list[dict[str, Any]] = Field(default_factory=list)
    disclaimer: str
    created_at: datetime
    updated_at: datetime


class LetterDraftSummary(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    template_kind: LetterTemplateKindLiteral
    workflow_status: LetterDraftWorkflowStatus
    issue_source_id: str | None
    version: int
    validation_ok: bool
    created_at: datetime
    updated_at: datetime


class LetterDraftListResponse(BaseSchema):
    items: list[LetterDraftSummary]
    templates: list[LetterDraftTemplateSummary]
