"""Admin-gated SAML certificate rotation processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.federation_metadata_models import SamlMetadataValidationStatus
from api.modules.enterprise.federation_metadata_repository import (
    SamlFederationMetadataUploadRepository,
)
from api.modules.enterprise.saml_cert_rotation_models import (
    SamlCertificateRotationRun,
    SamlCertificateRotationStatus,
)
from api.modules.enterprise.saml_cert_rotation_repository import (
    SamlCertificateRotationRunRepository,
)


@dataclass(frozen=True)
class SamlCertificateRotationRunSummary:
    run: SamlCertificateRotationRun
    completed_at: datetime


async def submit_saml_certificate_rotation_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    metadata_upload_id: uuid.UUID,
    rotation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    rotation_repo: SamlCertificateRotationRunRepository | None = None,
    metadata_repo: SamlFederationMetadataUploadRepository | None = None,
) -> SamlCertificateRotationRunSummary:
    rotations = rotation_repo or SamlCertificateRotationRunRepository(session)
    metadata = metadata_repo or SamlFederationMetadataUploadRepository(session)
    requested_at = rotations.utcnow()

    upload = await metadata.get_upload_by_id(metadata_upload_id)
    if upload is None or upload.organization_id != organization_id:
        raise ValueError("SAML federation metadata upload not found")
    if upload.validation_status != SamlMetadataValidationStatus.VALID:
        raise ValueError("SAML federation metadata upload is not valid")
    if not upload.entity_id:
        raise ValueError("SAML federation metadata upload is missing entity ID")

    run = await rotations.create_run(
        organization_id=organization_id,
        metadata_upload_id=upload.id,
        entity_id=upload.entity_id,
        status=SamlCertificateRotationStatus.PENDING_APPROVAL,
        rotation_summary=rotation_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return SamlCertificateRotationRunSummary(run=run, completed_at=requested_at)


async def approve_saml_certificate_rotation_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    rotation_repo: SamlCertificateRotationRunRepository | None = None,
) -> SamlCertificateRotationRunSummary:
    rotations = rotation_repo or SamlCertificateRotationRunRepository(session)
    approved_at = rotations.utcnow()

    run = await rotations.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("SAML certificate rotation run not found")
    if run.status != SamlCertificateRotationStatus.PENDING_APPROVAL:
        raise ValueError("SAML certificate rotation run is not pending approval")

    rotated_at = rotations.utcnow()
    run.status = SamlCertificateRotationStatus.ROTATED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.rotated_at = rotated_at
    await session.flush()
    await session.refresh(run)
    return SamlCertificateRotationRunSummary(run=run, completed_at=rotated_at)
