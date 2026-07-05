"""Pydantic schemas for admin-gated SAML automated rotation scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.saml_automated_rotation import SamlAutomatedRotationStatus as AutomatedGateStatus
from api.modules.enterprise.saml_automated_rotation_models import (
    SamlAutomatedRotationRun,
    SamlAutomatedRotationRunStatus,
)


class SamlAutomatedRotationStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    cert_rotation_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: AutomatedGateStatus) -> "SamlAutomatedRotationStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            cert_rotation_ready=status.cert_rotation_ready,
            blockers=list(status.blockers),
        )


class SamlAutomatedRotationSubmitRequest(BaseSchema):
    rotation_summary: str = Field(min_length=1, max_length=2000)


class SamlAutomatedRotationRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    saml_certificate_rotation_run_id: uuid.UUID
    entity_id: str
    status: SamlAutomatedRotationRunStatus
    rotation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    automated_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: SamlAutomatedRotationRun) -> "SamlAutomatedRotationRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            saml_certificate_rotation_run_id=run.saml_certificate_rotation_run_id,
            entity_id=run.entity_id,
            status=run.status,
            rotation_summary=run.rotation_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            automated_at=run.automated_at,
            error_message=run.error_message,
        )


class SamlAutomatedRotationRunResultResponse(BaseSchema):
    completed_at: datetime
    run: SamlAutomatedRotationRunResponse


class SamlAutomatedRotationRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
