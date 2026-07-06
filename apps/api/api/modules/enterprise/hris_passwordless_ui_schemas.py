"""Pydantic schemas for admin-gated HRIS passwordless UI scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.hris_passwordless_ui import HrisPasswordlessUiStatus as UiGateStatus
from api.core.responses import BaseSchema
from api.modules.enterprise.hris_passwordless_ui_models import (
    HrisPasswordlessUiRun,
    HrisPasswordlessUiRunStatus,
)


class HrisPasswordlessUiStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    passwordless_enrollment_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: UiGateStatus) -> "HrisPasswordlessUiStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            passwordless_enrollment_ready=status.passwordless_enrollment_ready,
            blockers=list(status.blockers),
        )


class HrisPasswordlessUiSubmitRequest(BaseSchema):
    ui_summary: str = Field(min_length=1, max_length=2000)


class HrisPasswordlessUiRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    saml_passwordless_enrollment_run_id: uuid.UUID
    entity_id: str
    status: HrisPasswordlessUiRunStatus
    ui_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: HrisPasswordlessUiRun) -> "HrisPasswordlessUiRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            saml_passwordless_enrollment_run_id=run.saml_passwordless_enrollment_run_id,
            entity_id=run.entity_id,
            status=run.status,
            ui_summary=run.ui_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            error_message=run.error_message,
        )


class HrisPasswordlessUiRunResultResponse(BaseSchema):
    completed_at: datetime
    run: HrisPasswordlessUiRunResponse


class HrisPasswordlessUiRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
