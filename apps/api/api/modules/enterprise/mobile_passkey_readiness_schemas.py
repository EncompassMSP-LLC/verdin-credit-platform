"""Pydantic schemas for admin-gated mobile passkey readiness scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.mobile_passkey_readiness import MobilePasskeyReadinessStatus as PasskeyGateStatus
from api.core.responses import BaseSchema
from api.modules.enterprise.mobile_passkey_readiness_models import (
    MobilePasskeyReadinessRun,
    MobilePasskeyReadinessRunStatus,
)


class MobilePasskeyReadinessStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    hris_passwordless_ui_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: PasskeyGateStatus) -> "MobilePasskeyReadinessStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            hris_passwordless_ui_ready=status.hris_passwordless_ui_ready,
            blockers=list(status.blockers),
        )


class MobilePasskeyReadinessSubmitRequest(BaseSchema):
    readiness_summary: str = Field(min_length=1, max_length=2000)


class MobilePasskeyReadinessRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    hris_passwordless_ui_run_id: uuid.UUID
    entity_id: str
    status: MobilePasskeyReadinessRunStatus
    readiness_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: MobilePasskeyReadinessRun) -> "MobilePasskeyReadinessRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            hris_passwordless_ui_run_id=run.hris_passwordless_ui_run_id,
            entity_id=run.entity_id,
            status=run.status,
            readiness_summary=run.readiness_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            error_message=run.error_message,
        )


class MobilePasskeyReadinessRunResultResponse(BaseSchema):
    completed_at: datetime
    run: MobilePasskeyReadinessRunResponse


class MobilePasskeyReadinessRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
