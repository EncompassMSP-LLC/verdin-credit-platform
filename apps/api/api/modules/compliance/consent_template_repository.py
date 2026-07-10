"""Repository for org-specific consent document templates."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.compliance.models import ConsentDocumentTemplate


class ConsentDocumentTemplateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key(
        self,
        *,
        organization_id: uuid.UUID,
        template_key: str,
    ) -> ConsentDocumentTemplate | None:
        query = select(ConsentDocumentTemplate).where(
            ConsentDocumentTemplate.organization_id == organization_id,
            ConsentDocumentTemplate.template_key == template_key,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ConsentDocumentTemplate]:
        query = (
            select(ConsentDocumentTemplate)
            .where(ConsentDocumentTemplate.organization_id == organization_id)
            .order_by(ConsentDocumentTemplate.template_key.asc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def create(self, template: ConsentDocumentTemplate) -> ConsentDocumentTemplate:
        self._session.add(template)
        await self._session.flush()
        await self._session.refresh(template)
        return template

    async def save(self, template: ConsentDocumentTemplate) -> ConsentDocumentTemplate:
        await self._session.flush()
        await self._session.refresh(template)
        return template
