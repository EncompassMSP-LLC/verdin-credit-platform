"""Pydantic schemas for admin-gated SAML passwordless enrollment scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.saml_passwordless_enrollment import (
    SamlPasswordlessEnrollmentStatus as EnrollmentGateStatus,
)
from api.modules.enterprise.saml_passwordless_enrollment_models import (
    SamlPasswordlessEnrollmentRun,
    SamlPasswordlessEnrollmentRunStatus,
)


class SamlPasswordlessEnrollmentStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    automated_rotation_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: EnrollmentGateStatus
    ) -> "SamlPasswordlessEnrollmentStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            automated_rotation_ready=status.automated_rotation_ready,
            blockers=list(status.blockers),
        )


class SamlPasswordlessEnrollmentSubmitRequest(BaseSchema):
    enrollment_summary: str = Field(min_length=1, max_length=2000)


class SamlPasswordlessEnrollmentRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    saml_automated_rotation_run_id: uuid.UUID
    entity_id: str
    status: SamlPasswordlessEnrollmentRunStatus
    enrollment_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    enrolled_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: SamlPasswordlessEnrollmentRun
    ) -> "SamlPasswordlessEnrollmentRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            saml_automated_rotation_run_id=run.saml_automated_rotation_run_id,
            entity_id=run.entity_id,
            status=run.status,
            enrollment_summary=run.enrollment_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            enrolled_at=run.enrolled_at,
            error_message=run.error_message,
        )


class SamlPasswordlessEnrollmentRunResultResponse(BaseSchema):
    completed_at: datetime
    run: SamlPasswordlessEnrollmentRunResponse


class SamlPasswordlessEnrollmentRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
