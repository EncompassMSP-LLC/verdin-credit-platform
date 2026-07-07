"""Admin-gated multi-IdP bulk provisioning processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.bulk_idp_provisioning_models import (
    BulkIdpProvisioningRun,
    BulkIdpProvisioningRunStatus,
)
from api.modules.enterprise.bulk_idp_provisioning_repository import (
    BulkIdpProvisioningRunRepository,
)
from api.modules.enterprise.hris_passwordless_ui_models import HrisPasswordlessUiRunStatus
from api.modules.enterprise.hris_passwordless_ui_repository import HrisPasswordlessUiRunRepository


@dataclass(frozen=True)
class BulkIdpProvisioningRunSummary:
    run: BulkIdpProvisioningRun
    completed_at: datetime


async def submit_bulk_idp_provisioning_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    hris_passwordless_ui_run_id: uuid.UUID,
    provisioning_summary: str,
    requested_by_user_id: uuid.UUID | None,
    provisioning_repo: BulkIdpProvisioningRunRepository | None = None,
    ui_repo: HrisPasswordlessUiRunRepository | None = None,
) -> BulkIdpProvisioningRunSummary:
    provisioning_runs = provisioning_repo or BulkIdpProvisioningRunRepository(session)
    ui_runs = ui_repo or HrisPasswordlessUiRunRepository(session)
    requested_at = provisioning_runs.utcnow()

    ui_run = await ui_runs.get_run_by_id(hris_passwordless_ui_run_id)
    if ui_run is None or ui_run.organization_id != organization_id:
        raise ValueError("HRIS passwordless UI run not found")
    if ui_run.status != HrisPasswordlessUiRunStatus.APPROVED:
        raise ValueError("HRIS passwordless UI run is not approved")

    run = await provisioning_runs.create_run(
        organization_id=organization_id,
        hris_passwordless_ui_run_id=ui_run.id,
        entity_id=ui_run.entity_id,
        status=BulkIdpProvisioningRunStatus.PENDING_APPROVAL,
        provisioning_summary=provisioning_summary,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return BulkIdpProvisioningRunSummary(run=run, completed_at=requested_at)


async def approve_bulk_idp_provisioning_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    provisioning_repo: BulkIdpProvisioningRunRepository | None = None,
) -> BulkIdpProvisioningRunSummary:
    provisioning_runs = provisioning_repo or BulkIdpProvisioningRunRepository(session)
    approved_at = provisioning_runs.utcnow()

    run = await provisioning_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Bulk IdP provisioning run not found")
    if run.status != BulkIdpProvisioningRunStatus.PENDING_APPROVAL:
        raise ValueError("Bulk IdP provisioning run is not pending approval")

    provisioned_at = provisioning_runs.utcnow()
    run.status = BulkIdpProvisioningRunStatus.PROVISIONED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.provisioned_at = provisioned_at
    await session.flush()
    await session.refresh(run)
    return BulkIdpProvisioningRunSummary(run=run, completed_at=provisioned_at)
