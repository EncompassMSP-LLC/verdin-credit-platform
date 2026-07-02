"""Reporting repository — read-optimized aggregate queries."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_letter_models import DisputeLetter
from api.modules.accounts.models import Account
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client, ClientStatus
from api.modules.notifications.models import Notification


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
        model: type[Account] | type[DisputeLetter],
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
