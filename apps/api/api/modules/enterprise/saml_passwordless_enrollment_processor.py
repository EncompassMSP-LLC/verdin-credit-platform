"""Admin-gated SAML passwordless enrollment processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.saml_automated_rotation_models import SamlAutomatedRotationRunStatus
from api.modules.enterprise.saml_automated_rotation_repository import (
    SamlAutomatedRotationRunRepository,
)
from api.modules.enterprise.saml_passwordless_enrollment_models import (
    SamlPasswordlessEnrollmentRun,
    SamlPasswordlessEnrollmentRunStatus,
)
from api.modules.enterprise.saml_passwordless_enrollment_repository import (
    SamlPasswordlessEnrollmentRunRepository,
)


@dataclass(frozen=True)
class SamlPasswordlessEnrollmentRunSummary:
    run: SamlPasswordlessEnrollmentRun
    completed_at: datetime


async def submit_saml_passwordless_enrollment_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    saml_automated_rotation_run_id: uuid.UUID,
    enrollment_summary: str,
    requested_by_user_id: uuid.UUID | None,
    enrollment_repo: SamlPasswordlessEnrollmentRunRepository | None = None,
    automated_repo: SamlAutomatedRotationRunRepository | None = None,
) -> SamlPasswordlessEnrollmentRunSummary:
    enrollments = enrollment_repo or SamlPasswordlessEnrollmentRunRepository(session)
    automated_runs = automated_repo or SamlAutomatedRotationRunRepository(session)
    requested_at = enrollments.utcnow()

    automated_run = await automated_runs.get_run_by_id(saml_automated_rotation_run_id)
    if automated_run is None or automated_run.organization_id != organization_id:
        raise ValueError("SAML automated rotation run not found")
    if automated_run.status != SamlAutomatedRotationRunStatus.AUTOMATED:
        raise ValueError("SAML automated rotation run is not automated")

    run = await enrollments.create_run(
        organization_id=organization_id,
        saml_automated_rotation_run_id=automated_run.id,
        entity_id=automated_run.entity_id,
        status=SamlPasswordlessEnrollmentRunStatus.PENDING_APPROVAL,
        enrollment_summary=enrollment_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return SamlPasswordlessEnrollmentRunSummary(run=run, completed_at=requested_at)


async def approve_saml_passwordless_enrollment_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    enrollment_repo: SamlPasswordlessEnrollmentRunRepository | None = None,
) -> SamlPasswordlessEnrollmentRunSummary:
    enrollments = enrollment_repo or SamlPasswordlessEnrollmentRunRepository(session)
    approved_at = enrollments.utcnow()

    run = await enrollments.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("SAML passwordless enrollment run not found")
    if run.status != SamlPasswordlessEnrollmentRunStatus.PENDING_APPROVAL:
        raise ValueError("SAML passwordless enrollment run is not pending approval")

    enrolled_at = enrollments.utcnow()
    run.status = SamlPasswordlessEnrollmentRunStatus.ENROLLED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.enrolled_at = enrolled_at
    await session.flush()
    await session.refresh(run)
    return SamlPasswordlessEnrollmentRunSummary(run=run, completed_at=enrolled_at)
