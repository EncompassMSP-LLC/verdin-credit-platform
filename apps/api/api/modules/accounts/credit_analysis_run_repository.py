"""Repository for credit analysis runs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.credit_analysis_run_models import CreditAnalysisRun


class CreditAnalysisRunListFilters:
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


class CreditAnalysisRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        generated_by_id: uuid.UUID | None,
        status: str,
        schema_version: str,
        score_version: str,
        formula_version: str,
        inputs_hash: str,
        reports_evaluated: int,
        tradelines_evaluated: int,
        borrower_readiness_score: int,
        mortgage_readiness_score: int,
        band: str,
        payload: dict[str, Any],
        published_by_id: uuid.UUID | None = None,
    ) -> CreditAnalysisRun:
        now = datetime.now(UTC)
        row = CreditAnalysisRun(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=case_id,
            generated_by_id=generated_by_id,
            generated_at=now,
            status=status,
            published_at=now if status == "published" else None,
            published_by_id=published_by_id if status == "published" else None,
            schema_version=schema_version,
            score_version=score_version,
            formula_version=formula_version,
            inputs_hash=inputs_hash,
            reports_evaluated=reports_evaluated,
            tradelines_evaluated=tradelines_evaluated,
            borrower_readiness_score=borrower_readiness_score,
            mortgage_readiness_score=mortgage_readiness_score,
            band=band,
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
        status: str | None = None,
    ) -> CreditAnalysisRun | None:
        query = select(CreditAnalysisRun).where(
            CreditAnalysisRun.organization_id == organization_id,
            CreditAnalysisRun.case_id == case_id,
        )
        if status is not None:
            query = query.where(CreditAnalysisRun.status == status)
        result = await self._session.execute(
            query.order_by(CreditAnalysisRun.generated_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        run_id: uuid.UUID,
    ) -> CreditAnalysisRun | None:
        result = await self._session.execute(
            select(CreditAnalysisRun).where(
                CreditAnalysisRun.organization_id == organization_id,
                CreditAnalysisRun.case_id == case_id,
                CreditAnalysisRun.id == run_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_case(
        self,
        filters: CreditAnalysisRunListFilters,
    ) -> tuple[list[CreditAnalysisRun], int]:
        base = select(CreditAnalysisRun).where(
            CreditAnalysisRun.organization_id == filters.organization_id,
            CreditAnalysisRun.case_id == filters.case_id,
        )
        total = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        result = await self._session.execute(
            base.order_by(CreditAnalysisRun.generated_at.desc())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        return list(result.scalars().all()), int(total)
