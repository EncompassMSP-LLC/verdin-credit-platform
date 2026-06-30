"""Dispute letter repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_letter_models import DisputeLetter


class DisputeLetterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dispute_letter: DisputeLetter) -> DisputeLetter:
        self._session.add(dispute_letter)
        await self._session.flush()
        await self._session.refresh(dispute_letter)
        return dispute_letter

    async def list_for_account(
        self,
        *,
        organization_id: uuid.UUID,
        account_id: uuid.UUID,
    ) -> list[DisputeLetter]:
        result = await self._session.execute(
            select(DisputeLetter)
            .where(
                DisputeLetter.organization_id == organization_id,
                DisputeLetter.account_id == account_id,
                DisputeLetter.deleted_at.is_(None),
            )
            .order_by(DisputeLetter.created_at.desc())
        )
        return list(result.scalars().all())
