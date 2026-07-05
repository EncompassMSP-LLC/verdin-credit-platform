"""Repository for LLM dispute draft augment audit records."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_draft_augment_models import (
    LlmDisputeDraftAugment,
    LlmDisputeDraftAugmentStatus,
)


class LlmDisputeDraftAugmentListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class LlmDisputeDraftAugmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def create_augment(
        self,
        *,
        organization_id: uuid.UUID,
        account_id: uuid.UUID,
        case_id: uuid.UUID,
        recipient_type: str,
        base_template_id: str,
        base_subject: str,
        base_body: str,
        status: LlmDisputeDraftAugmentStatus,
        augmented_body: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        prompt_hash: str | None = None,
        requested_by_user_id: uuid.UUID | None = None,
        requested_at: datetime | None = None,
        completed_at: datetime | None = None,
        error_message: str | None = None,
    ) -> LlmDisputeDraftAugment:
        augment = LlmDisputeDraftAugment(
            organization_id=organization_id,
            account_id=account_id,
            case_id=case_id,
            recipient_type=recipient_type,
            base_template_id=base_template_id,
            base_subject=base_subject,
            base_body=base_body,
            augmented_body=augmented_body,
            status=status,
            provider=provider,
            model=model,
            prompt_hash=prompt_hash,
            requested_by_user_id=requested_by_user_id,
            requested_at=requested_at,
            completed_at=completed_at,
            error_message=error_message,
        )
        self._session.add(augment)
        await self._session.flush()
        await self._session.refresh(augment)
        return augment

    async def list_augments_for_account(
        self,
        organization_id: uuid.UUID,
        account_id: uuid.UUID,
        filters: LlmDisputeDraftAugmentListFilters,
    ) -> tuple[list[LlmDisputeDraftAugment], int]:
        base = (
            select(LlmDisputeDraftAugment)
            .where(LlmDisputeDraftAugment.organization_id == organization_id)
            .where(LlmDisputeDraftAugment.account_id == account_id)
            .order_by(LlmDisputeDraftAugment.requested_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(LlmDisputeDraftAugment)
            .where(LlmDisputeDraftAugment.organization_id == organization_id)
            .where(LlmDisputeDraftAugment.account_id == account_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
