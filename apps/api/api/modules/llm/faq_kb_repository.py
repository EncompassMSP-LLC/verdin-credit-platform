"""Repository for FAQ/KB conversation turns (LRP-405)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.faq_kb_models import FaqKbConversationTurn


class FaqKbRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, turn: FaqKbConversationTurn) -> FaqKbConversationTurn:
        self._session.add(turn)
        await self._session.flush()
        return turn

    async def save(self, turn: FaqKbConversationTurn) -> FaqKbConversationTurn:
        await self._session.flush()
        return turn

    async def get_by_id(
        self,
        turn_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> FaqKbConversationTurn | None:
        result = await self._session.execute(
            select(FaqKbConversationTurn).where(
                FaqKbConversationTurn.id == turn_id,
                FaqKbConversationTurn.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_org(
        self,
        *,
        organization_id: uuid.UUID,
        limit: int = 50,
    ) -> list[FaqKbConversationTurn]:
        result = await self._session.execute(
            select(FaqKbConversationTurn)
            .where(FaqKbConversationTurn.organization_id == organization_id)
            .order_by(FaqKbConversationTurn.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
