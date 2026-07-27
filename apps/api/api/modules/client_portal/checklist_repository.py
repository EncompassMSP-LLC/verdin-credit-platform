"""Repository for portal checklist completions."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.client_portal.checklist_models import PortalChecklistCompletion


class PortalChecklistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_case_user(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        portal_user_id: uuid.UUID,
    ) -> list[PortalChecklistCompletion]:
        result = await self._session.execute(
            select(PortalChecklistCompletion).where(
                PortalChecklistCompletion.organization_id == organization_id,
                PortalChecklistCompletion.case_id == case_id,
                PortalChecklistCompletion.portal_user_id == portal_user_id,
            )
        )
        return list(result.scalars().all())

    async def get_by_item_key(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        portal_user_id: uuid.UUID,
        item_key: str,
    ) -> PortalChecklistCompletion | None:
        result = await self._session.execute(
            select(PortalChecklistCompletion).where(
                PortalChecklistCompletion.organization_id == organization_id,
                PortalChecklistCompletion.case_id == case_id,
                PortalChecklistCompletion.portal_user_id == portal_user_id,
                PortalChecklistCompletion.item_key == item_key,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_status(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        portal_user_id: uuid.UUID,
        item_key: str,
        status: str,
    ) -> PortalChecklistCompletion:
        row = await self.get_by_item_key(
            organization_id=organization_id,
            case_id=case_id,
            portal_user_id=portal_user_id,
            item_key=item_key,
        )
        if row is None:
            row = PortalChecklistCompletion(
                organization_id=organization_id,
                case_id=case_id,
                portal_user_id=portal_user_id,
                item_key=item_key,
                status=status,
            )
            self._session.add(row)
        else:
            row.status = status
        await self._session.flush()
        return row
