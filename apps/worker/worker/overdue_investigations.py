"""Scan and escalate overdue CRA investigations from the worker."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from worker.metadata_tables import accounts_table
from worker.tasks import create_overdue_investigation_task
from worker.timeline import append_timeline_event

CRA_RESPONSE_DAYS = 30
DISPUTE_STATUS_AWAITING_RESPONSE = "awaiting_response"
INVESTIGATION_STATUS_PENDING = "pending"
INVESTIGATION_STATUS_OVERDUE = "overdue"
OVERDUE_NEXT_ACTION = "Escalate overdue investigation"
WORKER_SOURCE_MODULE = "worker.overdue_investigation_scan"


@dataclass(frozen=True, slots=True)
class OverdueScanResult:
    scanned: int
    escalated: int
    tasks_created: int


def _deadline_cutoff() -> date:
    return date.today() - timedelta(days=CRA_RESPONSE_DAYS)


def list_eligible_accounts(session: Session) -> list[Any]:
    cutoff = _deadline_cutoff()
    result = session.execute(
        select(accounts_table).where(
            accounts_table.c.deleted_at.is_(None),
            accounts_table.c.dispute_status == DISPUTE_STATUS_AWAITING_RESPONSE,
            accounts_table.c.investigation_status.in_(
                (INVESTIGATION_STATUS_PENDING, INVESTIGATION_STATUS_OVERDUE)
            ),
            accounts_table.c.last_dispute_date.isnot(None),
            accounts_table.c.last_dispute_date <= cutoff,
        )
    )
    return list(result.mappings().all())


def _append_overdue_timeline_event(
    session: Session,
    account: Any,
    *,
    previous_investigation_status: str,
) -> None:
    append_timeline_event(
        session,
        organization_id=account["organization_id"],
        event_type="ACCOUNT_INVESTIGATION_OVERDUE",
        event_category="account",
        title="CRA investigation overdue",
        description=(
            f"CRA investigation for '{account['creditor_name']}' is overdue — "
            "escalation task created by scheduled worker scan."
        ),
        source_module=WORKER_SOURCE_MODULE,
        case_id=account["case_id"],
        account_id=account["id"],
        metadata={
            "previous_investigation_status": previous_investigation_status,
            "investigation_status": INVESTIGATION_STATUS_OVERDUE,
            "dispute_status": account["dispute_status"],
        },
    )


def escalate_overdue_account(session: Session, account: Any) -> tuple[bool, bool]:
    """Mark overdue and ensure escalation task exists.

    Returns ``(status_changed, task_created)``.
    """
    task_created = create_overdue_investigation_task(
        session,
        organization_id=account["organization_id"],
        case_id=account["case_id"],
        account_id=account["id"],
        creditor_name=account["creditor_name"],
    )

    if account["investigation_status"] == INVESTIGATION_STATUS_OVERDUE:
        return False, task_created

    previous_status = account["investigation_status"]
    now = datetime.now(UTC)
    session.execute(
        update(accounts_table)
        .where(accounts_table.c.id == account["id"])
        .values(
            investigation_status=INVESTIGATION_STATUS_OVERDUE,
            ai_recommended_next_action=OVERDUE_NEXT_ACTION,
            updated_at=now,
        )
    )
    _append_overdue_timeline_event(
        session,
        account,
        previous_investigation_status=previous_status,
    )
    return True, task_created


def scan_and_escalate_overdue_investigations(session: Session) -> OverdueScanResult:
    accounts = list_eligible_accounts(session)
    escalated = 0
    tasks_created = 0

    for account in accounts:
        status_changed, task_created = escalate_overdue_account(session, account)
        if status_changed:
            escalated += 1
        if task_created:
            tasks_created += 1

    return OverdueScanResult(
        scanned=len(accounts),
        escalated=escalated,
        tasks_created=tasks_created,
    )
