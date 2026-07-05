"""Pydantic schemas for admin-gated SAML certificate rotation scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.saml_certificate_rotation import SamlCertificateRotationStatus as RotationGateStatus
from api.modules.enterprise.saml_cert_rotation_models import (
    SamlCertificateRotationRun,
    SamlCertificateRotationStatus,
)


class SamlCertificateRotationStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    hris_sync_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: RotationGateStatus) -> "SamlCertificateRotationStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            hris_sync_ready=status.hris_sync_ready,
            blockers=list(status.blockers),
        )


class SamlCertificateRotationRequest(BaseSchema):
    rotation_summary: str = Field(min_length=1, max_length=2000)


class SamlCertificateRotationRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    metadata_upload_id: uuid.UUID
    entity_id: str
    status: SamlCertificateRotationStatus
    rotation_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    rotated_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: SamlCertificateRotationRun) -> "SamlCertificateRotationRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            metadata_upload_id=run.metadata_upload_id,
            entity_id=run.entity_id,
            status=run.status,
            rotation_summary=run.rotation_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            rotated_at=run.rotated_at,
            error_message=run.error_message,
        )


class SamlCertificateRotationRunResultResponse(BaseSchema):
    completed_at: datetime
    run: SamlCertificateRotationRunResponse


class SamlCertificateRotationRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
