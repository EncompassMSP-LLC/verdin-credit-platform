"""Persistence for issue evidence vault links (LRP-208A)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.issue_evidence_link_models import IssueEvidenceLink


class IssueEvidenceLinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        link_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID | None = None,
    ) -> IssueEvidenceLink | None:
        query = select(IssueEvidenceLink).where(
            IssueEvidenceLink.id == link_id,
            IssueEvidenceLink.organization_id == organization_id,
            IssueEvidenceLink.deleted_at.is_(None),
        )
        if case_id is not None:
            query = query.where(IssueEvidenceLink.case_id == case_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def find_active(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        source_id: str,
        document_id: uuid.UUID,
    ) -> IssueEvidenceLink | None:
        result = await self._session.execute(
            select(IssueEvidenceLink).where(
                IssueEvidenceLink.organization_id == organization_id,
                IssueEvidenceLink.case_id == case_id,
                IssueEvidenceLink.source_id == source_id,
                IssueEvidenceLink.document_id == document_id,
                IssueEvidenceLink.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        source_id: str | None = None,
    ) -> list[IssueEvidenceLink]:
        query = (
            select(IssueEvidenceLink)
            .where(
                IssueEvidenceLink.organization_id == organization_id,
                IssueEvidenceLink.case_id == case_id,
                IssueEvidenceLink.deleted_at.is_(None),
            )
            .order_by(IssueEvidenceLink.created_at.asc())
        )
        if source_id is not None:
            query = query.where(IssueEvidenceLink.source_id == source_id)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def create(self, link: IssueEvidenceLink) -> IssueEvidenceLink:
        self._session.add(link)
        await self._session.flush()
        return link

    async def soft_delete(self, link: IssueEvidenceLink, *, actor_id: uuid.UUID | None) -> None:
        link.deleted_at = datetime.now(UTC)
        link.updated_by_id = actor_id
        await self._session.flush()
