"""Admin-gated mobile passkey readiness processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.hris_passwordless_ui_models import HrisPasswordlessUiRunStatus
from api.modules.enterprise.hris_passwordless_ui_repository import HrisPasswordlessUiRunRepository
from api.modules.enterprise.mobile_passkey_readiness_models import (
    MobilePasskeyReadinessRun,
    MobilePasskeyReadinessRunStatus,
)
from api.modules.enterprise.mobile_passkey_readiness_repository import (
    MobilePasskeyReadinessRunRepository,
)


@dataclass(frozen=True)
class MobilePasskeyReadinessRunSummary:
    run: MobilePasskeyReadinessRun
    completed_at: datetime


async def submit_mobile_passkey_readiness_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    hris_passwordless_ui_run_id: uuid.UUID,
    readiness_summary: str,
    requested_by_user_id: uuid.UUID | None,
    passkey_repo: MobilePasskeyReadinessRunRepository | None = None,
    ui_repo: HrisPasswordlessUiRunRepository | None = None,
) -> MobilePasskeyReadinessRunSummary:
    passkey_runs = passkey_repo or MobilePasskeyReadinessRunRepository(session)
    ui_runs = ui_repo or HrisPasswordlessUiRunRepository(session)
    requested_at = passkey_runs.utcnow()

    ui_run = await ui_runs.get_run_by_id(hris_passwordless_ui_run_id)
    if ui_run is None or ui_run.organization_id != organization_id:
        raise ValueError("HRIS passwordless UI run not found")
    if ui_run.status != HrisPasswordlessUiRunStatus.APPROVED:
        raise ValueError("HRIS passwordless UI run is not approved")

    run = await passkey_runs.create_run(
        organization_id=organization_id,
        hris_passwordless_ui_run_id=ui_run.id,
        entity_id=ui_run.entity_id,
        status=MobilePasskeyReadinessRunStatus.PENDING_APPROVAL,
        readiness_summary=readiness_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return MobilePasskeyReadinessRunSummary(run=run, completed_at=requested_at)


async def approve_mobile_passkey_readiness_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    passkey_repo: MobilePasskeyReadinessRunRepository | None = None,
) -> MobilePasskeyReadinessRunSummary:
    passkey_runs = passkey_repo or MobilePasskeyReadinessRunRepository(session)
    approved_at = passkey_runs.utcnow()

    run = await passkey_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Mobile passkey readiness run not found")
    if run.status != MobilePasskeyReadinessRunStatus.PENDING_APPROVAL:
        raise ValueError("Mobile passkey readiness run is not pending approval")

    run.status = MobilePasskeyReadinessRunStatus.APPROVED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    await session.flush()
    await session.refresh(run)
    return MobilePasskeyReadinessRunSummary(run=run, completed_at=approved_at)
