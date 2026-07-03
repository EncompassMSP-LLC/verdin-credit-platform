"""Retention policy enforcement — soft-delete expired records per active policy."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.cases.models import Case
from api.modules.clients.models import Client
from api.modules.compliance.enforcement_repository import RetentionEnforcementRunRepository
from api.modules.compliance.models import (
    EnforcementRunStatus,
    EnforcementTriggerSource,
    RetentionEnforcementRun,
    RetentionPolicy,
    RetentionScope,
)
from api.modules.compliance.repository import RetentionPolicyListFilters, RetentionPolicyRepository
from api.modules.documents.models import Document
from api.modules.timeline.models import Communication

AUDIT_LOGS_DEFERRED_MESSAGE = (
    "Audit log retention purge is deferred; timeline events are append-only."
)


@dataclass(frozen=True, slots=True)
class EnforcementSummary:
    runs: list[RetentionEnforcementRun]
    policies_processed: int
    items_enforced: int


async def _enforce_documents(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    cutoff: datetime,
) -> tuple[int, int]:
    base = select(Document.id).where(
        Document.organization_id == organization_id,
        Document.deleted_at.is_(None),
        Document.created_at < cutoff,
    )
    scanned = int(
        (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    )
    if scanned == 0:
        return 0, 0

    now = datetime.now(UTC)
    await session.execute(
        update(Document)
        .where(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
            Document.created_at < cutoff,
        )
        .values(deleted_at=now, updated_at=now)
    )
    return scanned, scanned


async def _enforce_communications(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    cutoff: datetime,
) -> tuple[int, int]:
    base = (
        select(Communication.id)
        .join(Case, Communication.case_id == Case.id)
        .where(
            Case.organization_id == organization_id,
            Communication.deleted_at.is_(None),
            Communication.created_at < cutoff,
        )
    )
    scanned = int(
        (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    )
    if scanned == 0:
        return 0, 0

    comm_ids = list((await session.execute(base)).scalars().all())
    now = datetime.now(UTC)
    await session.execute(
        update(Communication)
        .where(Communication.id.in_(comm_ids))
        .values(deleted_at=now, updated_at=now)
    )
    return scanned, scanned


async def _enforce_client_profiles(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    cutoff: datetime,
) -> tuple[int, int]:
    base = select(Client.id).where(
        Client.organization_id == organization_id,
        Client.deleted_at.is_(None),
        Client.created_at < cutoff,
    )
    scanned = int(
        (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    )
    if scanned == 0:
        return 0, 0

    now = datetime.now(UTC)
    await session.execute(
        update(Client)
        .where(
            Client.organization_id == organization_id,
            Client.deleted_at.is_(None),
            Client.created_at < cutoff,
        )
        .values(deleted_at=now, updated_at=now)
    )
    return scanned, scanned


async def _enforce_policy_scope(
    session: AsyncSession,
    policy: RetentionPolicy,
) -> tuple[int, int, EnforcementRunStatus, str | None]:
    cutoff = datetime.now(UTC) - timedelta(days=policy.retention_days)

    if policy.scope == RetentionScope.DOCUMENTS:
        scanned, enforced = await _enforce_documents(
            session,
            organization_id=policy.organization_id,
            cutoff=cutoff,
        )
        return scanned, enforced, EnforcementRunStatus.COMPLETED, None
    if policy.scope == RetentionScope.COMMUNICATIONS:
        scanned, enforced = await _enforce_communications(
            session,
            organization_id=policy.organization_id,
            cutoff=cutoff,
        )
        return scanned, enforced, EnforcementRunStatus.COMPLETED, None
    if policy.scope == RetentionScope.CLIENT_PROFILES:
        scanned, enforced = await _enforce_client_profiles(
            session,
            organization_id=policy.organization_id,
            cutoff=cutoff,
        )
        return scanned, enforced, EnforcementRunStatus.COMPLETED, None
    if policy.scope == RetentionScope.AUDIT_LOGS:
        return 0, 0, EnforcementRunStatus.SKIPPED, AUDIT_LOGS_DEFERRED_MESSAGE

    return 0, 0, EnforcementRunStatus.SKIPPED, f"Unsupported retention scope: {policy.scope}"


async def enforce_retention_policies_for_organization(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    trigger_source: EnforcementTriggerSource,
    retention_repo: RetentionPolicyRepository | None = None,
    run_repo: RetentionEnforcementRunRepository | None = None,
) -> EnforcementSummary:
    """Apply all active retention policies for an organization and record audit runs."""
    retention_repo = retention_repo or RetentionPolicyRepository(session)
    run_repo = run_repo or RetentionEnforcementRunRepository(session)

    policies, _ = await retention_repo.list_policies(
        RetentionPolicyListFilters(
            organization_id=organization_id,
            is_active=True,
            skip=0,
            limit=500,
        )
    )

    runs: list[RetentionEnforcementRun] = []
    total_enforced = 0

    for policy in policies:
        started_at = datetime.now(UTC)
        try:
            scanned, enforced, status, error_message = await _enforce_policy_scope(session, policy)
        except Exception as exc:  # noqa: BLE001 — audit failed runs
            completed_at = datetime.now(UTC)
            run = RetentionEnforcementRun(
                organization_id=organization_id,
                policy_id=policy.id,
                scope=policy.scope,
                trigger_source=trigger_source,
                status=EnforcementRunStatus.FAILED,
                items_scanned=0,
                items_enforced=0,
                started_at=started_at,
                completed_at=completed_at,
                error_message=str(exc),
            )
            run = await run_repo.create(run)
            runs.append(run)
            continue

        completed_at = datetime.now(UTC)
        run = RetentionEnforcementRun(
            organization_id=organization_id,
            policy_id=policy.id,
            scope=policy.scope,
            trigger_source=trigger_source,
            status=status,
            items_scanned=scanned,
            items_enforced=enforced,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
        )
        run = await run_repo.create(run)
        runs.append(run)
        total_enforced += enforced

    return EnforcementSummary(
        runs=runs,
        policies_processed=len(policies),
        items_enforced=total_enforced,
    )
