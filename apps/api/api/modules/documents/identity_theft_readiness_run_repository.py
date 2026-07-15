"""Repository for persisted FCRA §605B submission-readiness audit runs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.identity_theft_readiness_run_models import (
    IdentityTheft605bReadinessRun,
)


class ReadinessRunListFilters:
    def __init__(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        skip: int,
        limit: int,
    ) -> None:
        self.organization_id = organization_id
        self.case_id = case_id
        self.skip = skip
        self.limit = limit


class IdentityTheft605bReadinessRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        generated_by_id: uuid.UUID | None,
        is_ready: bool,
        packet_readiness: int | None,
        confirmed_count: int,
        attestation_recorded: bool,
        payload: dict[str, Any],
    ) -> IdentityTheft605bReadinessRun:
        row = IdentityTheft605bReadinessRun(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=case_id,
            generated_by_id=generated_by_id,
            generated_at=datetime.now(UTC),
            is_ready=is_ready,
            packet_readiness=packet_readiness,
            confirmed_count=confirmed_count,
            attestation_recorded=attestation_recorded,
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
    ) -> IdentityTheft605bReadinessRun | None:
        result = await self._session.execute(
            select(IdentityTheft605bReadinessRun)
            .where(
                IdentityTheft605bReadinessRun.organization_id == organization_id,
                IdentityTheft605bReadinessRun.case_id == case_id,
            )
            .order_by(IdentityTheft605bReadinessRun.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_case(
        self,
        filters: ReadinessRunListFilters,
    ) -> tuple[list[IdentityTheft605bReadinessRun], int]:
        base = (
            select(IdentityTheft605bReadinessRun)
            .where(
                IdentityTheft605bReadinessRun.organization_id == filters.organization_id,
                IdentityTheft605bReadinessRun.case_id == filters.case_id,
            )
            .order_by(IdentityTheft605bReadinessRun.generated_at.desc())
        )
        count_query = (
            select(func.count())
            .select_from(IdentityTheft605bReadinessRun)
            .where(
                IdentityTheft605bReadinessRun.organization_id == filters.organization_id,
                IdentityTheft605bReadinessRun.case_id == filters.case_id,
            )
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
