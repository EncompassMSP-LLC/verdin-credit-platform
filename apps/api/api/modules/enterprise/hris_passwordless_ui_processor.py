"""Admin-gated HRIS passwordless UI processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.hris_passwordless_ui_models import (
    HrisPasswordlessUiRun,
    HrisPasswordlessUiRunStatus,
)
from api.modules.enterprise.hris_passwordless_ui_repository import HrisPasswordlessUiRunRepository
from api.modules.enterprise.saml_passwordless_enrollment_models import (
    SamlPasswordlessEnrollmentRunStatus,
)
from api.modules.enterprise.saml_passwordless_enrollment_repository import (
    SamlPasswordlessEnrollmentRunRepository,
)


@dataclass(frozen=True)
class HrisPasswordlessUiRunSummary:
    run: HrisPasswordlessUiRun
    completed_at: datetime


async def submit_hris_passwordless_ui_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    saml_passwordless_enrollment_run_id: uuid.UUID,
    ui_summary: str,
    requested_by_user_id: uuid.UUID | None,
    ui_repo: HrisPasswordlessUiRunRepository | None = None,
    enrollment_repo: SamlPasswordlessEnrollmentRunRepository | None = None,
) -> HrisPasswordlessUiRunSummary:
    ui_runs = ui_repo or HrisPasswordlessUiRunRepository(session)
    enrollments = enrollment_repo or SamlPasswordlessEnrollmentRunRepository(session)
    requested_at = ui_runs.utcnow()

    enrollment_run = await enrollments.get_run_by_id(saml_passwordless_enrollment_run_id)
    if enrollment_run is None or enrollment_run.organization_id != organization_id:
        raise ValueError("SAML passwordless enrollment run not found")
    if enrollment_run.status != SamlPasswordlessEnrollmentRunStatus.ENROLLED:
        raise ValueError("SAML passwordless enrollment run is not enrolled")

    run = await ui_runs.create_run(
        organization_id=organization_id,
        saml_passwordless_enrollment_run_id=enrollment_run.id,
        entity_id=enrollment_run.entity_id,
        status=HrisPasswordlessUiRunStatus.PENDING_APPROVAL,
        ui_summary=ui_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return HrisPasswordlessUiRunSummary(run=run, completed_at=requested_at)


async def approve_hris_passwordless_ui_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    ui_repo: HrisPasswordlessUiRunRepository | None = None,
) -> HrisPasswordlessUiRunSummary:
    ui_runs = ui_repo or HrisPasswordlessUiRunRepository(session)
    approved_at = ui_runs.utcnow()

    run = await ui_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("HRIS passwordless UI run not found")
    if run.status != HrisPasswordlessUiRunStatus.PENDING_APPROVAL:
        raise ValueError("HRIS passwordless UI run is not pending approval")

    run.status = HrisPasswordlessUiRunStatus.APPROVED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    await session.flush()
    await session.refresh(run)
    return HrisPasswordlessUiRunSummary(run=run, completed_at=approved_at)
