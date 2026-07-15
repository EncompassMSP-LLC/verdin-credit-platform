"""Repository for persisted dispute response records (Phase 10)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_response_models import (
    DisputeResponse,
    DisputeResponseMethod,
    DisputeResponseOutcome,
)


class DisputeResponseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        account_id: uuid.UUID,
        outcome: DisputeResponseOutcome,
        response_method: DisputeResponseMethod,
        dispute_letter_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
        response_date: date | None = None,
        notes: str | None = None,
        recorded_by_id: uuid.UUID | None = None,
    ) -> DisputeResponse:
        row = DisputeResponse(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=case_id,
            account_id=account_id,
            dispute_letter_id=dispute_letter_id,
            document_id=document_id,
            outcome=outcome,
            response_method=response_method,
            response_date=response_date,
            recorded_at=datetime.now(UTC),
            notes=notes,
            created_by_id=recorded_by_id,
            updated_by_id=recorded_by_id,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def list_for_account(
        self,
        *,
        organization_id: uuid.UUID,
        account_id: uuid.UUID,
    ) -> list[DisputeResponse]:
        result = await self._session.execute(
            select(DisputeResponse)
            .where(
                DisputeResponse.organization_id == organization_id,
                DisputeResponse.account_id == account_id,
                DisputeResponse.deleted_at.is_(None),
            )
            .order_by(DisputeResponse.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def list_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[DisputeResponse]:
        result = await self._session.execute(
            select(DisputeResponse)
            .where(
                DisputeResponse.organization_id == organization_id,
                DisputeResponse.case_id == case_id,
                DisputeResponse.deleted_at.is_(None),
            )
            .order_by(DisputeResponse.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def count_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(DisputeResponse)
            .where(
                DisputeResponse.organization_id == organization_id,
                DisputeResponse.case_id == case_id,
                DisputeResponse.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())
