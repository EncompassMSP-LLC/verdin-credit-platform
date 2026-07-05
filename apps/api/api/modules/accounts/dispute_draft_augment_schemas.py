"""Pydantic schemas for LLM dispute draft augment scaffold."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from api.core.llm_dispute_draft_augment import LlmDisputeDraftAugmentStatus as AugmentGateStatus
from api.core.responses import BaseSchema
from api.modules.accounts.dispute_draft_augment_models import (
    LlmDisputeDraftAugment,
    LlmDisputeDraftAugmentStatus,
)


class LlmDisputeDraftAugmentStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    llm_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: AugmentGateStatus) -> "LlmDisputeDraftAugmentStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            llm_ready=status.llm_ready,
            blockers=list(status.blockers),
        )


class LlmDisputeDraftAugmentRequest(BaseSchema):
    recipient_type: Literal["credit_bureau", "furnisher"] = "credit_bureau"


class LlmDisputeDraftAugmentResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID
    recipient_type: str
    base_template_id: str
    base_subject: str
    base_body: str
    augmented_body: str | None
    status: LlmDisputeDraftAugmentStatus
    provider: str | None
    model: str | None
    prompt_hash: str | None
    requested_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    pii_scrubbed: bool = True

    @classmethod
    def from_model(cls, augment: LlmDisputeDraftAugment) -> "LlmDisputeDraftAugmentResponse":
        return cls(
            id=augment.id,
            organization_id=augment.organization_id,
            account_id=augment.account_id,
            case_id=augment.case_id,
            recipient_type=augment.recipient_type,
            base_template_id=augment.base_template_id,
            base_subject=augment.base_subject,
            base_body=augment.base_body,
            augmented_body=augment.augmented_body,
            status=augment.status,
            provider=augment.provider,
            model=augment.model,
            prompt_hash=augment.prompt_hash,
            requested_by_user_id=augment.requested_by_user_id,
            requested_at=augment.requested_at,
            completed_at=augment.completed_at,
            error_message=augment.error_message,
        )


class LlmDisputeDraftAugmentListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
