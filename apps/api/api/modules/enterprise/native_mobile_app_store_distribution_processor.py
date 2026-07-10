"""Admin-gated native mobile app store distribution processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.native_mobile_app_store_distribution_models import (
    NativeMobileAppStoreDistributionRun,
    NativeMobileAppStoreDistributionRunStatus,
)
from api.modules.enterprise.native_mobile_app_store_distribution_repository import (
    NativeMobileAppStoreDistributionRunRepository,
)
from api.modules.enterprise.native_mobile_passkey_client_models import (
    NativeMobilePasskeyClientRunStatus,
)
from api.modules.enterprise.native_mobile_passkey_client_repository import (
    NativeMobilePasskeyClientRunRepository,
)


@dataclass(frozen=True)
class NativeMobileAppStoreDistributionRunSummary:
    run: NativeMobileAppStoreDistributionRun
    completed_at: datetime


async def submit_native_mobile_app_store_distribution_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    native_mobile_passkey_client_run_id: uuid.UUID,
    distribution_summary: str,
    store_target: str,
    requested_by_user_id: uuid.UUID | None,
    distribution_repo: NativeMobileAppStoreDistributionRunRepository | None = None,
    client_repo: NativeMobilePasskeyClientRunRepository | None = None,
) -> NativeMobileAppStoreDistributionRunSummary:
    distributions = distribution_repo or NativeMobileAppStoreDistributionRunRepository(session)
    client_runs = client_repo or NativeMobilePasskeyClientRunRepository(session)
    requested_at = distributions.utcnow()

    client_run = await client_runs.get_run_by_id(native_mobile_passkey_client_run_id)
    if client_run is None or client_run.organization_id != organization_id:
        raise ValueError("Native mobile passkey client run not found")
    if client_run.status != NativeMobilePasskeyClientRunStatus.APPROVED:
        raise ValueError("Native mobile passkey client run is not approved")

    run = await distributions.create_run(
        organization_id=organization_id,
        native_mobile_passkey_client_run_id=client_run.id,
        entity_id=client_run.entity_id,
        status=NativeMobileAppStoreDistributionRunStatus.PENDING_APPROVAL,
        distribution_summary=distribution_summary,
        platform=client_run.platform,
        store_target=store_target,
        requested_by_user_id=requested_by_user_id,
        requested_at=requested_at,
    )
    return NativeMobileAppStoreDistributionRunSummary(run=run, completed_at=requested_at)


async def approve_native_mobile_app_store_distribution_run(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    run_id: uuid.UUID,
    approved_by_user_id: uuid.UUID | None,
    distribution_repo: NativeMobileAppStoreDistributionRunRepository | None = None,
) -> NativeMobileAppStoreDistributionRunSummary:
    distributions = distribution_repo or NativeMobileAppStoreDistributionRunRepository(session)
    approved_at = distributions.utcnow()

    run = await distributions.get_run_by_id(run_id)
    if run is None or run.organization_id != organization_id:
        raise ValueError("Native mobile app store distribution run not found")
    if run.status != NativeMobileAppStoreDistributionRunStatus.PENDING_APPROVAL:
        raise ValueError("Native mobile app store distribution run is not pending approval")

    ready_at = distributions.utcnow()
    run.status = NativeMobileAppStoreDistributionRunStatus.READY
    run.approved_by_user_id = approved_by_user_id
    run.approved_at = approved_at
    run.ready_at = ready_at
    await session.flush()
    await session.refresh(run)
    return NativeMobileAppStoreDistributionRunSummary(run=run, completed_at=ready_at)
