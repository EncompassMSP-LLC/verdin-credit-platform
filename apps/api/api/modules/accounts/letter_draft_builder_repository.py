"""Repository for Intelligent Letter Draft Builder (LRP-406)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.letter_draft_builder_models import (
    IntelligentLetterDraft,
    LetterDraftWorkflowStatus,
)


class LetterDraftBuilderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, draft: IntelligentLetterDraft) -> IntelligentLetterDraft:
        self._session.add(draft)
        await self._session.flush()
        await self._session.refresh(draft)
        return draft

    async def get_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        draft_id: uuid.UUID,
    ) -> IntelligentLetterDraft | None:
        result = await self._session.execute(
            select(IntelligentLetterDraft).where(
                IntelligentLetterDraft.id == draft_id,
                IntelligentLetterDraft.organization_id == organization_id,
                IntelligentLetterDraft.case_id == case_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        limit: int = 50,
    ) -> list[IntelligentLetterDraft]:
        result = await self._session.execute(
            select(IntelligentLetterDraft)
            .where(
                IntelligentLetterDraft.organization_id == organization_id,
                IntelligentLetterDraft.case_id == case_id,
            )
            .order_by(IntelligentLetterDraft.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def save(self, draft: IntelligentLetterDraft) -> IntelligentLetterDraft:
        await self._session.flush()
        await self._session.refresh(draft)
        return draft


def snapshot_version(draft: IntelligentLetterDraft) -> dict[str, Any]:
    return {
        "version": draft.version,
        "workflow_status": (
            draft.workflow_status.value
            if isinstance(draft.workflow_status, LetterDraftWorkflowStatus)
            else str(draft.workflow_status)
        ),
        "sections": draft.sections,
        "full_text": draft.full_text,
        "validation": draft.validation,
    }
