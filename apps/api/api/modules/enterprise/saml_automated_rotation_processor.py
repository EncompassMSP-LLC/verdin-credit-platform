"""Admin-gated SAML automated rotation processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.saml_automated_rotation_models import (
    SamlAutomatedRotationRun,
    SamlAutomatedRotationRunStatus,
)
from api.modules.enterprise.saml_automated_rotation_repository import (
    SamlAutomatedRotationRunRepository,
)
from api.modules.enterprise.saml_cert_rotation_models import SamlCertificateRotationStatus
from api.modules.enterprise.saml_cert_rotation_repository import (
    SamlCertificateRotationRunRepository,
)


@dataclass(frozen=True)
class SamlAutomatedRotationRunSummary:
    run: SamlAutomatedRotationRun
    completed_at: datetime


async def submit_saml_automated_rotation_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    saml_certificate_rotation_run_id: uuid.UUID,
    rotation_summary: str,
    requested_by_user_id: uuid.UUID | None,
    automated_repo: SamlAutomatedRotationRunRepository | None = None,
    rotation_repo: SamlCertificateRotationRunRepository | None = None,
) -> SamlAutomatedRotationRunSummary:
    automated_runs = automated_repo or SamlAutomatedRotationRunRepository(session)
    rotations = rotation_repo or SamlCertificateRotationRunRepository(session)
    requested_at = automated_runs.utcnow()

    rotation_run = await rotations.get_run_by_id(saml_certificate_rotation_run_id)
    if rotation_run is None or rotation_run.organization_id != organization_id:
        raise ValueError("SAML certificate rotation run not found")
    if rotation_run.status != SamlCertificateRotationStatus.ROTATED:
        raise ValueError("SAML certificate rotation run is not rotated")

    run = await automated_runs.create_run(
        organization_id=organization_id,
        saml_certificate_rotation_run_id=rotation_run.id,
        entity_id=rotation_run.entity_id,
        status=SamlAutomatedRotationRunStatus.PENDING_APPROVAL,
        rotation_summary=rotation_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return SamlAutomatedRotationRunSummary(run=run, completed_at=requested_at)


async def approve_saml_automated_rotation_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    automated_repo: SamlAutomatedRotationRunRepository | None = None,
) -> SamlAutomatedRotationRunSummary:
    automated_runs = automated_repo or SamlAutomatedRotationRunRepository(session)
    approved_at = automated_runs.utcnow()

    run = await automated_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("SAML automated rotation run not found")
    if run.status != SamlAutomatedRotationRunStatus.PENDING_APPROVAL:
        raise ValueError("SAML automated rotation run is not pending approval")

    automated_at = automated_runs.utcnow()
    run.status = SamlAutomatedRotationRunStatus.AUTOMATED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.automated_at = automated_at
    await session.flush()
    await session.refresh(run)
    return SamlAutomatedRotationRunSummary(run=run, completed_at=automated_at)
