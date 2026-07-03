"""Retention policy enforcement for the background worker."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session

from worker.compliance_tables import (
    cases_table,
    clients_table,
    communications_table,
    documents_table,
    retention_enforcement_runs_table,
    retention_policies_table,
)

AUDIT_LOGS_DEFERRED_MESSAGE = (
    "Audit log retention purge is deferred; timeline events are append-only."
)
SCOPE_AUDIT_LOGS = "audit_logs"
SCOPE_CLIENT_PROFILES = "client_profiles"
SCOPE_COMMUNICATIONS = "communications"
SCOPE_DOCUMENTS = "documents"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
TRIGGER_SCHEDULED = "scheduled"


@dataclass(frozen=True, slots=True)
class RetentionEnforcementScanResult:
    organizations_processed: int
    policies_processed: int
    items_enforced: int


def _list_target_organization_ids(
    session: Session, organization_id: uuid.UUID | None
) -> list[Any]:
    if organization_id is not None:
        return [organization_id]
    query = (
        select(retention_policies_table.c.organization_id)
        .where(
            retention_policies_table.c.deleted_at.is_(None),
            retention_policies_table.c.is_active.is_(True),
        )
        .distinct()
    )
    return list(session.execute(query).scalars().all())


def _list_active_policies(session: Session, organization_id: Any) -> list[Any]:
    result = session.execute(
        select(retention_policies_table).where(
            retention_policies_table.c.organization_id == organization_id,
            retention_policies_table.c.deleted_at.is_(None),
            retention_policies_table.c.is_active.is_(True),
        )
    )
    return list(result.mappings().all())


def _record_run(
    session: Session,
    *,
    organization_id: Any,
    policy: Any,
    trigger_source: str,
    status: str,
    items_scanned: int,
    items_enforced: int,
    started_at: datetime,
    completed_at: datetime,
    error_message: str | None,
) -> None:
    now = datetime.now(UTC)
    session.execute(
        insert(retention_enforcement_runs_table).values(
            id=uuid.uuid4(),
            organization_id=organization_id,
            policy_id=policy["id"],
            scope=policy["scope"],
            trigger_source=trigger_source,
            status=status,
            items_scanned=items_scanned,
            items_enforced=items_enforced,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
            created_at=now,
            updated_at=now,
        )
    )


def _enforce_documents(
    session: Session, *, organization_id: Any, cutoff: datetime
) -> tuple[int, int]:
    base = select(documents_table.c.id).where(
        documents_table.c.organization_id == organization_id,
        documents_table.c.deleted_at.is_(None),
        documents_table.c.created_at < cutoff,
    )
    scanned = int(
        session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    )
    if scanned == 0:
        return 0, 0
    now = datetime.now(UTC)
    result = session.execute(
        update(documents_table)
        .where(
            documents_table.c.organization_id == organization_id,
            documents_table.c.deleted_at.is_(None),
            documents_table.c.created_at < cutoff,
        )
        .values(deleted_at=now, updated_at=now)
    )
    return scanned, int(result.rowcount or 0)


def _enforce_communications(
    session: Session,
    *,
    organization_id: Any,
    cutoff: datetime,
) -> tuple[int, int]:
    base = (
        select(communications_table.c.id)
        .join(cases_table, communications_table.c.case_id == cases_table.c.id)
        .where(
            cases_table.c.organization_id == organization_id,
            communications_table.c.deleted_at.is_(None),
            communications_table.c.created_at < cutoff,
        )
    )
    scanned = int(
        session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    )
    if scanned == 0:
        return 0, 0
    comm_ids = list(session.execute(base).scalars().all())
    now = datetime.now(UTC)
    result = session.execute(
        update(communications_table)
        .where(communications_table.c.id.in_(comm_ids))
        .values(deleted_at=now, updated_at=now)
    )
    return scanned, int(result.rowcount or 0)


def _enforce_client_profiles(
    session: Session,
    *,
    organization_id: Any,
    cutoff: datetime,
) -> tuple[int, int]:
    base = select(clients_table.c.id).where(
        clients_table.c.organization_id == organization_id,
        clients_table.c.deleted_at.is_(None),
        clients_table.c.created_at < cutoff,
    )
    scanned = int(
        session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    )
    if scanned == 0:
        return 0, 0
    now = datetime.now(UTC)
    result = session.execute(
        update(clients_table)
        .where(
            clients_table.c.organization_id == organization_id,
            clients_table.c.deleted_at.is_(None),
            clients_table.c.created_at < cutoff,
        )
        .values(deleted_at=now, updated_at=now)
    )
    return scanned, int(result.rowcount or 0)


def _enforce_policy(session: Session, policy: Any) -> tuple[int, int, str, str | None]:
    cutoff = datetime.now(UTC) - timedelta(days=int(policy["retention_days"]))
    scope = policy["scope"]

    if scope == SCOPE_DOCUMENTS:
        scanned, enforced = _enforce_documents(
            session,
            organization_id=policy["organization_id"],
            cutoff=cutoff,
        )
        return scanned, enforced, STATUS_COMPLETED, None
    if scope == SCOPE_COMMUNICATIONS:
        scanned, enforced = _enforce_communications(
            session,
            organization_id=policy["organization_id"],
            cutoff=cutoff,
        )
        return scanned, enforced, STATUS_COMPLETED, None
    if scope == SCOPE_CLIENT_PROFILES:
        scanned, enforced = _enforce_client_profiles(
            session,
            organization_id=policy["organization_id"],
            cutoff=cutoff,
        )
        return scanned, enforced, STATUS_COMPLETED, None
    if scope == SCOPE_AUDIT_LOGS:
        return 0, 0, STATUS_SKIPPED, AUDIT_LOGS_DEFERRED_MESSAGE

    return 0, 0, STATUS_SKIPPED, f"Unsupported retention scope: {scope}"


def run_retention_enforcement_scan(
    session: Session,
    *,
    organization_id: uuid.UUID | None = None,
) -> RetentionEnforcementScanResult:
    """Apply active retention policies for one or all organizations."""
    org_ids = _list_target_organization_ids(session, organization_id)
    policies_processed = 0
    items_enforced = 0

    for org_id in org_ids:
        policies = _list_active_policies(session, org_id)
        for policy in policies:
            started_at = datetime.now(UTC)
            try:
                scanned, enforced, status, error_message = _enforce_policy(
                    session, policy
                )
            except Exception as exc:  # noqa: BLE001 — record failed audit runs
                completed_at = datetime.now(UTC)
                _record_run(
                    session,
                    organization_id=org_id,
                    policy=policy,
                    trigger_source=TRIGGER_SCHEDULED,
                    status=STATUS_FAILED,
                    items_scanned=0,
                    items_enforced=0,
                    started_at=started_at,
                    completed_at=completed_at,
                    error_message=str(exc),
                )
                policies_processed += 1
                continue

            completed_at = datetime.now(UTC)
            _record_run(
                session,
                organization_id=org_id,
                policy=policy,
                trigger_source=TRIGGER_SCHEDULED,
                status=status,
                items_scanned=scanned,
                items_enforced=enforced,
                started_at=started_at,
                completed_at=completed_at,
                error_message=error_message,
            )
            policies_processed += 1
            items_enforced += enforced

    return RetentionEnforcementScanResult(
        organizations_processed=len(org_ids),
        policies_processed=policies_processed,
        items_enforced=items_enforced,
    )
