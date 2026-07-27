"""Repository for consultation pack runs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.cases.consultation_pack_models import ConsultationPackRun


class ConsultationPackRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        generated_by_id: uuid.UUID | None,
        schema_version: str,
        credit_analysis_run_id: uuid.UUID | None,
        payload: dict[str, Any],
    ) -> ConsultationPackRun:
        now = datetime.now(UTC)
        row = ConsultationPackRun(
            organization_id=organization_id,
            case_id=case_id,
            generated_by_id=generated_by_id,
            generated_at=now,
            status="draft",
            schema_version=schema_version,
            credit_analysis_run_id=credit_analysis_run_id,
            payload=payload,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        run_id: uuid.UUID,
    ) -> ConsultationPackRun | None:
        result = await self._session.execute(
            select(ConsultationPackRun).where(
                ConsultationPackRun.organization_id == organization_id,
                ConsultationPackRun.case_id == case_id,
                ConsultationPackRun.id == run_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> ConsultationPackRun | None:
        result = await self._session.execute(
            select(ConsultationPackRun)
            .where(
                ConsultationPackRun.organization_id == organization_id,
                ConsultationPackRun.case_id == case_id,
            )
            .order_by(ConsultationPackRun.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ConsultationPackRun], int]:
        base = select(ConsultationPackRun).where(
            ConsultationPackRun.organization_id == organization_id,
            ConsultationPackRun.case_id == case_id,
        )
        total = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        result = await self._session.execute(
            base.order_by(ConsultationPackRun.generated_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), int(total)
