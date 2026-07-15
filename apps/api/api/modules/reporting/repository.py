"""Reporting repository — read-optimized aggregate queries."""

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any, cast

from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.materialized_reporting import (
    BUREAU_ACCOUNT_MV,
    BUREAU_SENT_LETTERS_MV,
    TEAM_PRODUCTIVITY_MV,
)
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.dispute_response_models import DisputeResponse
from api.modules.accounts.models import Account, AccountBureau, DisputeStatus
from api.modules.auth.models import User
from api.modules.cases.models import Case, CaseStatus
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client, ClientStatus
from api.modules.notifications.models import Notification
from api.modules.tasks.models import Task, TaskStatus


class OperationsReportingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_operations_summary(self, organization_id: uuid.UUID) -> dict[str, Any]:
        now = datetime.now(UTC)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        clients = await self._get_client_metrics(organization_id)
        dispute_accounts = await self._count_by_enum(
            Account,
            Account.dispute_status,
            organization_id=organization_id,
        )
        dispute_letters = await self._count_by_enum(
            DisputeLetter,
            DisputeLetter.status,
            organization_id=organization_id,
        )
        notifications = await self._get_notification_metrics(
            organization_id,
            start_of_day,
            end_of_day,
        )
        portal_users = await self._count_portal_users(organization_id)

        return {
            "clients": clients,
            "dispute_accounts": dispute_accounts,
            "dispute_letters": dispute_letters,
            "notifications": notifications,
            "portal_users": portal_users,
        }

    async def _count(self, query: Any) -> int:
        result = await self._session.execute(select(func.count()).select_from(query.subquery()))
        return int(result.scalar_one())

    async def _count_by_enum(
        self,
        model: type[Account] | type[DisputeLetter] | type[Case],
        status_column: Any,
        *,
        organization_id: uuid.UUID,
    ) -> dict[str, int]:
        base = and_(model.organization_id == organization_id, model.deleted_at.is_(None))
        result = await self._session.execute(
            select(status_column, func.count()).where(base).group_by(status_column)
        )
        return {row[0].value: int(row[1]) for row in result.all()}

    async def _get_client_metrics(self, organization_id: uuid.UUID) -> dict[str, int]:
        base = and_(Client.organization_id == organization_id, Client.deleted_at.is_(None))
        total = await self._count(select(Client).where(base))
        active = await self._count(select(Client).where(base, Client.status == ClientStatus.ACTIVE))
        portal_enabled = await self._count(
            select(ClientPortalUser).where(
                ClientPortalUser.organization_id == organization_id,
                ClientPortalUser.deleted_at.is_(None),
                ClientPortalUser.is_active.is_(True),
            )
        )
        return {
            "total": total,
            "active": active,
            "portal_enabled": portal_enabled,
        }

    async def _get_notification_metrics(
        self,
        organization_id: uuid.UUID,
        start_of_day: datetime,
        end_of_day: datetime,
    ) -> dict[str, int]:
        base = Notification.organization_id == organization_id
        unread_total = await self._count(
            select(Notification).where(base, Notification.read_at.is_(None))
        )
        created_today = await self._count(
            select(Notification).where(
                base,
                Notification.created_at >= start_of_day,
                Notification.created_at < end_of_day,
            )
        )
        return {
            "unread_total": unread_total,
            "created_today": created_today,
        }

    async def _count_portal_users(self, organization_id: uuid.UUID) -> int:
        return await self._count(
            select(ClientPortalUser).where(
                ClientPortalUser.organization_id == organization_id,
                ClientPortalUser.deleted_at.is_(None),
                ClientPortalUser.is_active.is_(True),
            )
        )

    async def get_reinvestigation_outcomes(
        self,
        organization_id: uuid.UUID,
        *,
        start: date | None = None,
        end: date | None = None,
        bureau: AccountBureau | None = None,
    ) -> list[dict[str, Any]]:
        """Recorded dispute-response outcomes for an org, reduced for analytics.

        Each row is ``{"outcome": str, "days_to_response": int | None}``.
        ``days_to_response`` is the elapsed days from the clock start (the linked
        sent letter's ``sent_at`` when present, else the account's
        ``last_dispute_date``) to the response date (``response_date`` when
        recorded, else ``recorded_at``). Read-only; no live bureau contact.

        Optional filters: ``bureau`` scopes to a single credit bureau (applied in
        SQL); ``start``/``end`` scope by response day inclusively (applied in
        Python, since the response day uses a ``recorded_at`` fallback).
        """
        conditions = [
            DisputeResponse.organization_id == organization_id,
            DisputeResponse.deleted_at.is_(None),
        ]
        if bureau is not None:
            conditions.append(Account.bureau == bureau)
        result = await self._session.execute(
            select(
                DisputeResponse.outcome,
                DisputeResponse.response_date,
                DisputeResponse.recorded_at,
                DisputeLetter.sent_at,
                Account.last_dispute_date,
            )
            .join(Account, Account.id == DisputeResponse.account_id)
            .outerjoin(DisputeLetter, DisputeLetter.id == DisputeResponse.dispute_letter_id)
            .where(*conditions)
        )
        rows: list[dict[str, Any]] = []
        for outcome, response_date, recorded_at, sent_at, last_dispute_date in result.all():
            start_day = sent_at.date() if sent_at is not None else last_dispute_date
            response_day = response_date if response_date is not None else recorded_at.date()
            if start is not None and (response_day is None or response_day < start):
                continue
            if end is not None and (response_day is None or response_day > end):
                continue
            days_to_response: int | None = None
            if start_day is not None and response_day is not None:
                elapsed = (response_day - start_day).days
                days_to_response = elapsed if elapsed >= 0 else None
            rows.append(
                {
                    "outcome": outcome.value if hasattr(outcome, "value") else str(outcome),
                    "days_to_response": days_to_response,
                }
            )
        return rows

    async def get_bureau_performance(self, organization_id: uuid.UUID) -> dict[str, Any]:
        account_rows = await self._session.execute(
            select(Account.bureau, Account.dispute_status, func.count())
            .where(Account.organization_id == organization_id, Account.deleted_at.is_(None))
            .group_by(Account.bureau, Account.dispute_status)
        )

        bureau_data: dict[str, dict[str, Any]] = {}
        total_accounts = 0
        for bureau, dispute_status, count in account_rows.all():
            bureau_key = bureau.value if hasattr(bureau, "value") else str(bureau)
            status_key = (
                dispute_status.value if hasattr(dispute_status, "value") else str(dispute_status)
            )
            entry = bureau_data.setdefault(
                bureau_key,
                {
                    "total_accounts": 0,
                    "dispute_status": {},
                    "sent_letters": 0,
                    "resolved_accounts": 0,
                },
            )
            entry["total_accounts"] += int(count)
            entry["dispute_status"][status_key] = int(count)
            total_accounts += int(count)
            if status_key in {
                DisputeStatus.CORRECTED.value,
                DisputeStatus.DELETED.value,
                DisputeStatus.VERIFIED.value,
            }:
                entry["resolved_accounts"] += int(count)

        letter_rows = await self._session.execute(
            select(Account.bureau, func.count())
            .join(DisputeLetter, DisputeLetter.account_id == Account.id)
            .where(
                DisputeLetter.organization_id == organization_id,
                DisputeLetter.deleted_at.is_(None),
                DisputeLetter.status == DisputeLetterStatus.SENT,
                Account.deleted_at.is_(None),
            )
            .group_by(Account.bureau)
        )
        for bureau, count in letter_rows.all():
            bureau_key = bureau.value if hasattr(bureau, "value") else str(bureau)
            entry = bureau_data.setdefault(
                bureau_key,
                {
                    "total_accounts": 0,
                    "dispute_status": {},
                    "sent_letters": 0,
                    "resolved_accounts": 0,
                },
            )
            entry["sent_letters"] = int(count)

        bureaus = []
        for bureau in AccountBureau:
            entry = bureau_data.get(
                bureau.value,
                {
                    "total_accounts": 0,
                    "dispute_status": {},
                    "sent_letters": 0,
                    "resolved_accounts": 0,
                },
            )
            if entry["total_accounts"] == 0 and entry["sent_letters"] == 0:
                continue
            bureaus.append({"bureau": bureau.value, **entry})

        return {"bureaus": bureaus, "total_accounts": total_accounts}

    async def get_team_productivity(self, organization_id: uuid.UUID) -> dict[str, Any]:
        now = datetime.now(UTC)
        window_start = now - timedelta(days=30)

        users_result = await self._session.execute(
            select(User).where(
                User.organization_id == organization_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        users = list(users_result.scalars().all())
        user_ids = {user.id for user in users}

        open_task_rows = await self._session.execute(
            select(Task.assigned_user_id, func.count())
            .where(
                Task.organization_id == organization_id,
                Task.deleted_at.is_(None),
                Task.assigned_user_id.is_not(None),
                Task.status.in_(
                    [TaskStatus.OPEN, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED],
                ),
            )
            .group_by(Task.assigned_user_id)
        )
        open_tasks_by_user = {
            row[0]: int(row[1]) for row in open_task_rows.all() if row[0] in user_ids
        }

        completed_task_rows = await self._session.execute(
            select(Task.completed_by_id, func.count())
            .where(
                Task.organization_id == organization_id,
                Task.deleted_at.is_(None),
                Task.completed_by_id.is_not(None),
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at.is_not(None),
                Task.completed_at >= window_start,
            )
            .group_by(Task.completed_by_id)
        )
        completed_tasks_by_user = {
            row[0]: int(row[1]) for row in completed_task_rows.all() if row[0] in user_ids
        }

        open_case_rows = await self._session.execute(
            select(Case.assigned_to_id, func.count())
            .where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                Case.assigned_to_id.is_not(None),
                Case.status.not_in([CaseStatus.CLOSED, CaseStatus.RESOLVED]),
            )
            .group_by(Case.assigned_to_id)
        )
        open_cases_by_user = {
            row[0]: int(row[1]) for row in open_case_rows.all() if row[0] in user_ids
        }

        closed_case_rows = await self._session.execute(
            select(Case.assigned_to_id, func.count())
            .where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                Case.assigned_to_id.is_not(None),
                Case.status.in_([CaseStatus.CLOSED, CaseStatus.RESOLVED]),
                Case.closed_at.is_not(None),
                Case.closed_at >= window_start,
            )
            .group_by(Case.assigned_to_id)
        )
        closed_cases_by_user = {
            row[0]: int(row[1]) for row in closed_case_rows.all() if row[0] in user_ids
        }

        members = []
        for user in users:
            members.append(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip(),
                    "open_tasks": open_tasks_by_user.get(user.id, 0),
                    "completed_tasks_30d": completed_tasks_by_user.get(user.id, 0),
                    "assigned_open_cases": open_cases_by_user.get(user.id, 0),
                    "closed_cases_30d": closed_cases_by_user.get(user.id, 0),
                }
            )

        members.sort(
            key=lambda item: (
                -cast(int, item["completed_tasks_30d"]),
                cast(str, item["full_name"]).lower(),
            )
        )

        return {
            "members": members,
            "open_tasks_total": sum(open_tasks_by_user.values()),
            "completed_tasks_30d_total": sum(completed_tasks_by_user.values()),
            "assigned_open_cases_total": sum(open_cases_by_user.values()),
            "closed_cases_30d_total": sum(closed_cases_by_user.values()),
        }

    async def get_bureau_performance_from_views(
        self,
        organization_id: uuid.UUID,
    ) -> dict[str, Any]:
        account_rows = await self._session.execute(
            text(
                f"""
                SELECT bureau, dispute_status, account_count
                FROM {BUREAU_ACCOUNT_MV}
                WHERE organization_id = :organization_id
                """
            ),
            {"organization_id": organization_id},
        )
        letter_rows = await self._session.execute(
            text(
                f"""
                SELECT bureau, sent_letter_count
                FROM {BUREAU_SENT_LETTERS_MV}
                WHERE organization_id = :organization_id
                """
            ),
            {"organization_id": organization_id},
        )

        bureau_data: dict[str, dict[str, Any]] = {}
        total_accounts = 0
        for bureau, dispute_status, count in account_rows.all():
            bureau_key = str(bureau)
            status_key = str(dispute_status)
            entry = bureau_data.setdefault(
                bureau_key,
                {
                    "total_accounts": 0,
                    "dispute_status": {},
                    "sent_letters": 0,
                    "resolved_accounts": 0,
                },
            )
            account_count = int(count)
            entry["total_accounts"] += account_count
            entry["dispute_status"][status_key] = account_count
            total_accounts += account_count
            if status_key in {
                DisputeStatus.CORRECTED.value,
                DisputeStatus.DELETED.value,
                DisputeStatus.VERIFIED.value,
            }:
                entry["resolved_accounts"] += account_count

        for bureau, count in letter_rows.all():
            bureau_key = str(bureau)
            entry = bureau_data.setdefault(
                bureau_key,
                {
                    "total_accounts": 0,
                    "dispute_status": {},
                    "sent_letters": 0,
                    "resolved_accounts": 0,
                },
            )
            entry["sent_letters"] = int(count)

        bureaus = []
        for bureau in AccountBureau:
            entry = bureau_data.get(
                bureau.value,
                {
                    "total_accounts": 0,
                    "dispute_status": {},
                    "sent_letters": 0,
                    "resolved_accounts": 0,
                },
            )
            if entry["total_accounts"] == 0 and entry["sent_letters"] == 0:
                continue
            bureaus.append({"bureau": bureau.value, **entry})

        return {"bureaus": bureaus, "total_accounts": total_accounts}

    async def get_team_productivity_from_views(
        self,
        organization_id: uuid.UUID,
    ) -> dict[str, Any]:
        metric_rows = await self._session.execute(
            text(
                f"""
                SELECT
                    user_id,
                    open_tasks,
                    completed_tasks_30d,
                    assigned_open_cases,
                    closed_cases_30d
                FROM {TEAM_PRODUCTIVITY_MV}
                WHERE organization_id = :organization_id
                """
            ),
            {"organization_id": organization_id},
        )
        metrics_by_user = {
            row[0]: {
                "open_tasks": int(row[1]),
                "completed_tasks_30d": int(row[2]),
                "assigned_open_cases": int(row[3]),
                "closed_cases_30d": int(row[4]),
            }
            for row in metric_rows.all()
        }

        users_result = await self._session.execute(
            select(User).where(
                User.organization_id == organization_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        users = list(users_result.scalars().all())

        members = []
        for user in users:
            metrics = metrics_by_user.get(
                user.id,
                {
                    "open_tasks": 0,
                    "completed_tasks_30d": 0,
                    "assigned_open_cases": 0,
                    "closed_cases_30d": 0,
                },
            )
            members.append(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip(),
                    **metrics,
                }
            )

        members.sort(
            key=lambda item: (
                -cast(int, item["completed_tasks_30d"]),
                cast(str, item["full_name"]).lower(),
            )
        )

        return {
            "members": members,
            "open_tasks_total": sum(item["open_tasks"] for item in members),
            "completed_tasks_30d_total": sum(item["completed_tasks_30d"] for item in members),
            "assigned_open_cases_total": sum(item["assigned_open_cases"] for item in members),
            "closed_cases_30d_total": sum(item["closed_cases_30d"] for item in members),
        }

    async def get_historical_outcome_raw(self, organization_id: uuid.UUID) -> dict[str, Any]:
        now = datetime.now(UTC)
        start_30d = now - timedelta(days=30)
        start_90d = now - timedelta(days=90)

        cases_by_status = await self._count_by_enum(
            Case,
            Case.status,
            organization_id=organization_id,
        )
        accounts_by_dispute_status = await self._count_by_enum(
            Account,
            Account.dispute_status,
            organization_id=organization_id,
        )
        dispute_letters_by_status = await self._count_by_enum(
            DisputeLetter,
            DisputeLetter.status,
            organization_id=organization_id,
        )

        case_base = and_(
            Case.organization_id == organization_id,
            Case.deleted_at.is_(None),
            Case.status.in_([CaseStatus.RESOLVED, CaseStatus.CLOSED]),
        )
        cases_closed_30d = await self._count(
            select(Case).where(
                case_base,
                Case.closed_at.is_not(None),
                Case.closed_at >= start_30d,
            )
        )
        cases_closed_90d = await self._count(
            select(Case).where(
                case_base,
                Case.closed_at.is_not(None),
                Case.closed_at >= start_90d,
            )
        )

        resolved_statuses = [DisputeStatus.CORRECTED, DisputeStatus.DELETED]
        accounts_dispute_resolved = await self._count(
            select(Account).where(
                Account.organization_id == organization_id,
                Account.deleted_at.is_(None),
                Account.dispute_status.in_(resolved_statuses),
            )
        )
        dispute_letters_sent = dispute_letters_by_status.get(DisputeLetterStatus.SENT.value, 0)

        return {
            "cases_by_status": cases_by_status,
            "accounts_by_dispute_status": accounts_by_dispute_status,
            "dispute_letters_by_status": dispute_letters_by_status,
            "cases_closed_30d": cases_closed_30d,
            "cases_closed_90d": cases_closed_90d,
            "accounts_dispute_resolved": accounts_dispute_resolved,
            "dispute_letters_sent": dispute_letters_sent,
        }
