"""Case repository — owns all Case database access."""

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.cases.schemas import CaseSortField, CaseSortOrder


@dataclass(frozen=True, slots=True)
class CaseListFilters:
    organization_id: uuid.UUID
    search: str | None = None
    status: CaseStatus | None = None
    stage: CaseStage | None = None
    priority: CasePriority | None = None
    assigned_user_id: uuid.UUID | None = None
    skip: int = 0
    limit: int = 20
    sort_by: CaseSortField = "created_at"
    sort_order: CaseSortOrder = "desc"


_SORT_COLUMNS: dict[CaseSortField, InstrumentedAttribute[Any]] = {
    "created_at": Case.created_at,
    "updated_at": Case.updated_at,
    "title": Case.title,
    "status": Case.status,
    "stage": Case.stage,
    "priority": Case.priority,
    "opened_at": Case.opened_at,
    "case_number": Case.case_number,
}


class CaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        case_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Case | None:
        uid = uuid.UUID(str(case_id))
        query = select(Case).where(Case.id == uid, Case.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Case.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_case_number(self, case_number: str) -> Case | None:
        result = await self._session.execute(
            select(Case).where(
                Case.case_number == case_number,
                Case.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_cases(self, filters: CaseListFilters) -> tuple[list[Case], int]:
        base = select(Case).where(
            Case.organization_id == filters.organization_id,
            Case.deleted_at.is_(None),
        )

        if filters.status is not None:
            base = base.where(Case.status == filters.status)
        if filters.stage is not None:
            base = base.where(Case.stage == filters.stage)
        if filters.priority is not None:
            base = base.where(Case.priority == filters.priority)
        if filters.assigned_user_id is not None:
            base = base.where(Case.assigned_to_id == filters.assigned_user_id)
        if filters.search:
            term = f"%{filters.search.strip()}%"
            base = base.where(
                or_(
                    Case.title.ilike(term),
                    Case.client_name.ilike(term),
                    Case.client_email.ilike(term),
                    Case.case_number.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()

        result = await self._session.execute(
            base.order_by(order).offset(filters.skip).limit(filters.limit)
        )
        return list(result.scalars().all()), total

    async def create(self, case: Case) -> Case:
        self._session.add(case)
        await self._session.flush()
        await self._session.refresh(case)
        return case

    async def update(self, case: Case) -> Case:
        await self._session.flush()
        await self._session.refresh(case)
        return case
