"""Worker-side task persistence helpers."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Column, DateTime, Enum, String, Table, Text, insert, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from worker.metadata_tables import metadata as worker_metadata
from worker.timeline import append_timeline_event

PARSED_REPORT_REVIEW_TASK_SOURCE = "documents.parsed_credit_report"
OVERDUE_INVESTIGATION_TASK_SOURCE = "accounts.dispute_investigation_overdue"
_TERMINAL_STATUSES = ("completed", "canceled")

tasks_table = Table(
    "tasks",
    worker_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), nullable=False),
    Column("case_id", UUID(as_uuid=True)),
    Column("account_id", UUID(as_uuid=True)),
    Column("document_id", UUID(as_uuid=True)),
    Column("assigned_user_id", UUID(as_uuid=True)),
    Column("title", String(255), nullable=False),
    Column("description", Text),
    Column(
        "status",
        Enum(
            "open",
            "in_progress",
            "blocked",
            "completed",
            "canceled",
            name="task_status",
        ),
    ),
    Column("priority", Enum("low", "medium", "high", "critical", name="task_priority")),
    Column("due_date", DateTime(timezone=True)),
    Column("completed_at", DateTime(timezone=True)),
    Column("completed_by_id", UUID(as_uuid=True)),
    Column("source_module", String(50)),
    Column("source_event_id", UUID(as_uuid=True)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("deleted_at", DateTime(timezone=True)),
    Column("created_by_id", UUID(as_uuid=True)),
    Column("updated_by_id", UUID(as_uuid=True)),
)


def _account_candidate_count(parsed_report: dict[str, Any]) -> int:
    accounts = parsed_report.get("accounts")
    if not isinstance(accounts, list):
        return 0
    return sum(1 for account in accounts if isinstance(account, dict))


def create_parsed_report_review_task(
    session: Session,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    account_id: uuid.UUID | None,
    document_id: uuid.UUID,
    document_title: str,
    parsed_report_id: uuid.UUID,
    parsed_report: dict[str, Any],
) -> uuid.UUID | None:
    """Create or reuse the active review task for a parsed credit report."""

    candidate_count = _account_candidate_count(parsed_report)
    if candidate_count == 0:
        return None

    existing = session.execute(
        select(tasks_table.c.id).where(
            tasks_table.c.organization_id == organization_id,
            tasks_table.c.document_id == document_id,
            tasks_table.c.source_module == PARSED_REPORT_REVIEW_TASK_SOURCE,
            tasks_table.c.source_event_id == parsed_report_id,
            tasks_table.c.status.notin_(_TERMINAL_STATUSES),
            tasks_table.c.deleted_at.is_(None),
        )
    ).one_or_none()
    if existing is not None:
        return existing.id

    now = datetime.now(UTC)
    task_id = uuid.uuid4()
    session.execute(
        insert(tasks_table).values(
            id=task_id,
            organization_id=organization_id,
            case_id=case_id,
            account_id=account_id,
            document_id=document_id,
            assigned_user_id=None,
            title=f"Review {candidate_count} account candidate(s) from {document_title}",
            description=(
                "Review parsed credit report tradelines and create account records "
                "for candidate tradelines that should be tracked."
            ),
            status="open",
            priority="high",
            due_date=now + timedelta(days=1),
            completed_at=None,
            completed_by_id=None,
            source_module=PARSED_REPORT_REVIEW_TASK_SOURCE,
            source_event_id=parsed_report_id,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            created_by_id=None,
            updated_by_id=None,
        )
    )
    append_timeline_event(
        session,
        organization_id=organization_id,
        event_type="TASK_CREATED",
        event_category="task",
        title="Review task created",
        description="Automated task created for parsed credit report account review.",
        source_module="worker",
        case_id=case_id,
        account_id=account_id,
        document_id=document_id,
        metadata={
            "task_id": str(task_id),
            "source_module": PARSED_REPORT_REVIEW_TASK_SOURCE,
            "source_event_id": str(parsed_report_id),
            "candidate_count": candidate_count,
        },
    )
    return task_id


def create_overdue_investigation_task(
    session: Session,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    account_id: uuid.UUID,
    creditor_name: str,
) -> bool:
    """Create or reuse the active overdue investigation escalation task."""

    existing = session.execute(
        select(tasks_table.c.id).where(
            tasks_table.c.organization_id == organization_id,
            tasks_table.c.account_id == account_id,
            tasks_table.c.source_module == OVERDUE_INVESTIGATION_TASK_SOURCE,
            tasks_table.c.source_event_id == account_id,
            tasks_table.c.status.notin_(_TERMINAL_STATUSES),
            tasks_table.c.deleted_at.is_(None),
        )
    ).one_or_none()
    if existing is not None:
        return False

    now = datetime.now(UTC)
    task_id = uuid.uuid4()
    session.execute(
        insert(tasks_table).values(
            id=task_id,
            organization_id=organization_id,
            case_id=case_id,
            account_id=account_id,
            document_id=None,
            assigned_user_id=None,
            title=f"Escalate overdue CRA investigation for {creditor_name}",
            description=(
                "The statutory CRA investigation window has passed without a recorded response. "
                "Escalate with the bureau or furnisher and document next steps."
            ),
            status="open",
            priority="high",
            due_date=now + timedelta(days=2),
            completed_at=None,
            completed_by_id=None,
            source_module=OVERDUE_INVESTIGATION_TASK_SOURCE,
            source_event_id=account_id,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            created_by_id=None,
            updated_by_id=None,
        )
    )
    append_timeline_event(
        session,
        organization_id=organization_id,
        event_type="TASK_CREATED",
        event_category="task",
        title="Overdue investigation task created",
        description="Automated escalation task created for overdue CRA investigation.",
        source_module="worker",
        case_id=case_id,
        account_id=account_id,
        metadata={
            "task_id": str(task_id),
            "source_module": OVERDUE_INVESTIGATION_TASK_SOURCE,
            "source_event_id": str(account_id),
        },
    )
    return True
