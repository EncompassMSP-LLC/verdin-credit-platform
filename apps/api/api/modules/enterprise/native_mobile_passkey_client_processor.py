"""Admin-gated native mobile passkey client processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.mobile_passkey_readiness_models import MobilePasskeyReadinessRunStatus
from api.modules.enterprise.mobile_passkey_readiness_repository import (
    MobilePasskeyReadinessRunRepository,
)
from api.modules.enterprise.native_mobile_passkey_client_models import (
    NativeMobilePasskeyClientRun,
    NativeMobilePasskeyClientRunStatus,
)
from api.modules.enterprise.native_mobile_passkey_client_repository import (
    NativeMobilePasskeyClientRunRepository,
)


@dataclass(frozen=True)
class NativeMobilePasskeyClientRunSummary:
    run: NativeMobilePasskeyClientRun
    completed_at: datetime


async def submit_native_mobile_passkey_client_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    mobile_passkey_readiness_run_id: uuid.UUID,
    client_summary: str,
    platform: str,
    requested_by_user_id: uuid.UUID | None,
    client_repo: NativeMobilePasskeyClientRunRepository | None = None,
    readiness_repo: MobilePasskeyReadinessRunRepository | None = None,
) -> NativeMobilePasskeyClientRunSummary:
    client_runs = client_repo or NativeMobilePasskeyClientRunRepository(session)
    readiness_runs = readiness_repo or MobilePasskeyReadinessRunRepository(session)
    requested_at = client_runs.utcnow()

    readiness_run = await readiness_runs.get_run_by_id(mobile_passkey_readiness_run_id)
    if readiness_run is None or readiness_run.organization_id != organization_id:
        raise ValueError("Mobile passkey readiness run not found")
    if readiness_run.status != MobilePasskeyReadinessRunStatus.APPROVED:
        raise ValueError("Mobile passkey readiness run is not approved")

    run = await client_runs.create_run(
        organization_id=organization_id,
        mobile_passkey_readiness_run_id=readiness_run.id,
        entity_id=readiness_run.entity_id,
        status=NativeMobilePasskeyClientRunStatus.PENDING_APPROVAL,
        client_summary=client_summary,
        platform=platform,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return NativeMobilePasskeyClientRunSummary(run=run, completed_at=requested_at)


async def approve_native_mobile_passkey_client_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    client_repo: NativeMobilePasskeyClientRunRepository | None = None,
) -> NativeMobilePasskeyClientRunSummary:
    client_runs = client_repo or NativeMobilePasskeyClientRunRepository(session)
    approved_at = client_runs.utcnow()

    run = await client_runs.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Native mobile passkey client run not found")
    if run.status != NativeMobilePasskeyClientRunStatus.PENDING_APPROVAL:
        raise ValueError("Native mobile passkey client run is not pending approval")

    run.status = NativeMobilePasskeyClientRunStatus.APPROVED
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    await session.flush()
    await session.refresh(run)
    return NativeMobilePasskeyClientRunSummary(run=run, completed_at=approved_at)
