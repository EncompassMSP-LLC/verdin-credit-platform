"""Repository for persisted dispute-strategy runs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.strategy_run_models import DisputeStrategyRun


class StrategyRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        generated_by_id: uuid.UUID | None,
        accounts_planned: int,
        issues_covered: int,
        payload: dict[str, Any],
    ) -> DisputeStrategyRun:
        row = DisputeStrategyRun(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=case_id,
            generated_by_id=generated_by_id,
            generated_at=datetime.now(UTC),
            accounts_planned=accounts_planned,
            issues_covered=issues_covered,
            payload=payload,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def get_latest_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> DisputeStrategyRun | None:
        result = await self._session.execute(
            select(DisputeStrategyRun)
            .where(
                DisputeStrategyRun.organization_id == organization_id,
                DisputeStrategyRun.case_id == case_id,
            )
            .order_by(DisputeStrategyRun.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
