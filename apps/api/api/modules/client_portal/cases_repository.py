"""Read-only case queries scoped to a portal client."""

import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.models import Account
from api.modules.cases.models import Case
from api.modules.clients.models import Client, ClientContact


class ClientPortalCasesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_cases_for_client(
        self,
        *,
        organization_id: uuid.UUID,
        client: Client,
        portal_email: str,
        contact_emails: list[str],
    ) -> list[Case]:
        match_conditions = self._build_match_conditions(
            client=client,
            portal_email=portal_email,
            contact_emails=contact_emails,
        )
        if not match_conditions:
            return []

        result = await self._session.execute(
            select(Case)
            .where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                or_(*match_conditions),
            )
            .order_by(Case.opened_at.desc())
        )
        return list(result.scalars().all())

    async def get_case_for_client(
        self,
        case_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        client: Client,
        portal_email: str,
        contact_emails: list[str],
    ) -> Case | None:
        match_conditions = self._build_match_conditions(
            client=client,
            portal_email=portal_email,
            contact_emails=contact_emails,
        )
        if not match_conditions:
            return None

        result = await self._session.execute(
            select(Case).where(
                Case.id == case_id,
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                or_(*match_conditions),
            )
        )
        return result.scalar_one_or_none()

    async def count_accounts_by_dispute_status(
        self,
        case_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> dict[str, int]:
        result = await self._session.execute(
            select(Account.dispute_status, func.count())
            .where(
                Account.case_id == case_id,
                Account.organization_id == organization_id,
                Account.deleted_at.is_(None),
            )
            .group_by(Account.dispute_status)
        )
        return {row[0].value: int(row[1]) for row in result.all()}

    @staticmethod
    def _build_match_conditions(
        *,
        client: Client,
        portal_email: str,
        contact_emails: list[str],
    ) -> list[Any]:
        conditions: list[Any] = [
            func.lower(Case.client_email) == portal_email.lower(),
            func.lower(Case.client_name) == client.display_name.lower(),
        ]
        if client.email:
            conditions.append(func.lower(Case.client_email) == client.email.lower())

        normalized_contact_emails = {email.lower() for email in contact_emails if email}
        if normalized_contact_emails:
            conditions.append(func.lower(Case.client_email).in_(normalized_contact_emails))
        return conditions

    async def list_contact_emails(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> list[str]:
        result = await self._session.execute(
            select(ClientContact.email).where(
                ClientContact.organization_id == organization_id,
                ClientContact.client_id == client_id,
                ClientContact.deleted_at.is_(None),
                ClientContact.email.is_not(None),
            )
        )
        return [email for email in result.scalars().all() if email]
