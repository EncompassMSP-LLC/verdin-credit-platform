"""Repository for dispute-strategy checklist staff overrides."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.modules.documents.checklist_override_models import DisputeStrategyChecklistOverride


class ChecklistOverrideRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        checklist_kind: str,
    ) -> list[DisputeStrategyChecklistOverride]:
        result = await self._session.execute(
            select(DisputeStrategyChecklistOverride).where(
                DisputeStrategyChecklistOverride.organization_id == organization_id,
                DisputeStrategyChecklistOverride.case_id == case_id,
                DisputeStrategyChecklistOverride.checklist_kind == checklist_kind,
                DisputeStrategyChecklistOverride.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_including_deleted(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        checklist_kind: str,
        account_key: str,
        item_id: str,
    ) -> DisputeStrategyChecklistOverride | None:
        result = await self._session.execute(
            select(DisputeStrategyChecklistOverride).where(
                DisputeStrategyChecklistOverride.organization_id == organization_id,
                DisputeStrategyChecklistOverride.case_id == case_id,
                DisputeStrategyChecklistOverride.checklist_kind == checklist_kind,
                DisputeStrategyChecklistOverride.account_key == account_key,
                DisputeStrategyChecklistOverride.item_id == item_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        checklist_kind: str,
        account_key: str,
        item_id: str,
        completion_status: str,
        note: str | None,
        user_id: uuid.UUID | None,
    ) -> DisputeStrategyChecklistOverride:
        existing = await self.get_including_deleted(
            organization_id=organization_id,
            case_id=case_id,
            checklist_kind=checklist_kind,
            account_key=account_key,
            item_id=item_id,
        )
        cleaned_note = note.strip() if isinstance(note, str) and note.strip() else None
        if existing is None:
            row = DisputeStrategyChecklistOverride(
                organization_id=organization_id,
                case_id=case_id,
                checklist_kind=checklist_kind,
                account_key=account_key,
                item_id=item_id,
                completion_status=completion_status,
                note=cleaned_note,
            )
            apply_audit_on_create(row, user_id)
            self._session.add(row)
            await self._session.flush()
            await self._session.refresh(row)
            return row

        existing.completion_status = completion_status
        existing.note = cleaned_note
        existing.deleted_at = None
        apply_audit_on_update(existing, user_id)
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def clear(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        checklist_kind: str,
        account_key: str,
        item_id: str,
        user_id: uuid.UUID | None,
    ) -> DisputeStrategyChecklistOverride | None:
        existing = await self.get_including_deleted(
            organization_id=organization_id,
            case_id=case_id,
            checklist_kind=checklist_kind,
            account_key=account_key,
            item_id=item_id,
        )
        if existing is None or existing.deleted_at is not None:
            return existing
        existing.soft_delete()
        apply_audit_on_update(existing, user_id)
        await self._session.flush()
        await self._session.refresh(existing)
        return existing
