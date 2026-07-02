"""Compliance center repository — consent and retention database access."""

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.compliance.models import (
    ConsentRecord,
    ConsentStatus,
    ConsentType,
    RetentionPolicy,
    RetentionScope,
)
from api.modules.compliance.schemas import (
    ConsentSortField,
    ConsentSortOrder,
    RetentionSortField,
    RetentionSortOrder,
)


@dataclass(frozen=True, slots=True)
class ConsentListFilters:
    organization_id: uuid.UUID
    client_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None
    consent_type: ConsentType | None = None
    status: ConsentStatus | None = None
    skip: int = 0
    limit: int = 20
    sort_by: ConsentSortField = "granted_at"
    sort_order: ConsentSortOrder = "desc"


@dataclass(frozen=True, slots=True)
class RetentionPolicyListFilters:
    organization_id: uuid.UUID
    scope: RetentionScope | None = None
    is_active: bool | None = None
    skip: int = 0
    limit: int = 20
    sort_by: RetentionSortField = "created_at"
    sort_order: RetentionSortOrder = "desc"


_CONSENT_SORT_COLUMNS: dict[ConsentSortField, InstrumentedAttribute[Any]] = {
    "granted_at": ConsentRecord.granted_at,
    "created_at": ConsentRecord.created_at,
    "consent_type": ConsentRecord.consent_type,
    "status": ConsentRecord.status,
}

_RETENTION_SORT_COLUMNS: dict[RetentionSortField, InstrumentedAttribute[Any]] = {
    "created_at": RetentionPolicy.created_at,
    "name": RetentionPolicy.name,
    "scope": RetentionPolicy.scope,
    "retention_days": RetentionPolicy.retention_days,
}


class ConsentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        consent_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> ConsentRecord | None:
        query = select(ConsentRecord).where(
            ConsentRecord.id == consent_id,
            ConsentRecord.organization_id == organization_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_consents(self, filters: ConsentListFilters) -> tuple[list[ConsentRecord], int]:
        base = select(ConsentRecord).where(ConsentRecord.organization_id == filters.organization_id)
        if filters.client_id is not None:
            base = base.where(ConsentRecord.client_id == filters.client_id)
        if filters.case_id is not None:
            base = base.where(ConsentRecord.case_id == filters.case_id)
        if filters.consent_type is not None:
            base = base.where(ConsentRecord.consent_type == filters.consent_type)
        if filters.status is not None:
            base = base.where(ConsentRecord.status == filters.status)

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _CONSENT_SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        query = base.order_by(order).offset(filters.skip).limit(filters.limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, record: ConsentRecord) -> ConsentRecord:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def save(self, record: ConsentRecord) -> ConsentRecord:
        await self._session.flush()
        await self._session.refresh(record)
        return record


class RetentionPolicyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        policy_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> RetentionPolicy | None:
        query = select(RetentionPolicy).where(
            RetentionPolicy.id == policy_id,
            RetentionPolicy.organization_id == organization_id,
            RetentionPolicy.deleted_at.is_(None),
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_policies(
        self,
        filters: RetentionPolicyListFilters,
    ) -> tuple[list[RetentionPolicy], int]:
        base = select(RetentionPolicy).where(
            RetentionPolicy.organization_id == filters.organization_id,
            RetentionPolicy.deleted_at.is_(None),
        )
        if filters.scope is not None:
            base = base.where(RetentionPolicy.scope == filters.scope)
        if filters.is_active is not None:
            base = base.where(RetentionPolicy.is_active == filters.is_active)

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _RETENTION_SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        query = base.order_by(order).offset(filters.skip).limit(filters.limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, policy: RetentionPolicy) -> RetentionPolicy:
        self._session.add(policy)
        await self._session.flush()
        await self._session.refresh(policy)
        return policy

    async def save(self, policy: RetentionPolicy) -> RetentionPolicy:
        await self._session.flush()
        await self._session.refresh(policy)
        return policy
