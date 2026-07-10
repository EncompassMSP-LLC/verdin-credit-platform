"""Account repository — owns all Account database access."""

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.accounts.intelligence import CRITICAL_RISK_THRESHOLD
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    DisputeStatus,
    PaymentStatus,
)
from api.modules.accounts.schemas import AccountSortField, AccountSortOrder
from api.modules.cases.models import Case


@dataclass(frozen=True, slots=True)
class AccountListFilters:
    organization_id: uuid.UUID
    search: str | None = None
    case_id: uuid.UUID | None = None
    client_id: uuid.UUID | None = None
    bureau: AccountBureau | None = None
    account_type: AccountType | None = None
    account_status: AccountStatus | None = None
    payment_status: PaymentStatus | None = None
    dispute_status: DisputeStatus | None = None
    min_risk_score: int | None = None
    max_risk_score: int | None = None
    min_readiness_score: int | None = None
    dispute_ready: bool | None = None
    skip: int = 0
    limit: int = 20
    sort_by: AccountSortField = "created_at"
    sort_order: AccountSortOrder = "desc"


_SORT_COLUMNS: dict[AccountSortField, InstrumentedAttribute[Any]] = {
    "creditor_name": Account.creditor_name,
    "bureau": Account.bureau,
    "account_type": Account.account_type,
    "account_status": Account.account_status,
    "dispute_status": Account.dispute_status,
    "balance": Account.balance,
    "date_reported": Account.date_reported,
    "risk_score": Account.risk_score,
    "readiness_score": Account.readiness_score,
    "created_at": Account.created_at,
}


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_query(self, organization_id: uuid.UUID) -> Any:
        return select(Account).where(
            Account.organization_id == organization_id,
            Account.deleted_at.is_(None),
        )

    def _apply_list_filters(self, query: Any, filters: AccountListFilters) -> Any:
        if filters.client_id is not None:
            query = query.join(Case, Account.case_id == Case.id).where(
                Case.client_id == filters.client_id,
                Case.deleted_at.is_(None),
            )
        if filters.case_id is not None:
            query = query.where(Account.case_id == filters.case_id)
        if filters.bureau is not None:
            query = query.where(Account.bureau == filters.bureau)
        if filters.account_type is not None:
            query = query.where(Account.account_type == filters.account_type)
        if filters.account_status is not None:
            query = query.where(Account.account_status == filters.account_status)
        if filters.payment_status is not None:
            query = query.where(Account.payment_status == filters.payment_status)
        if filters.dispute_status is not None:
            query = query.where(Account.dispute_status == filters.dispute_status)
        if filters.min_risk_score is not None:
            query = query.where(Account.risk_score >= filters.min_risk_score)
        if filters.max_risk_score is not None:
            query = query.where(Account.risk_score <= filters.max_risk_score)
        if filters.min_readiness_score is not None:
            query = query.where(Account.readiness_score >= filters.min_readiness_score)
        if filters.dispute_ready:
            query = query.where(Account.dispute_status == DisputeStatus.READY_FOR_DISPUTE)
        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = query.where(
                or_(
                    Account.creditor_name.ilike(term),
                    Account.original_creditor.ilike(term),
                    Account.account_number_masked.ilike(term),
                    Account.remarks.ilike(term),
                )
            )
        return query

    async def get_by_id(
        self,
        account_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Account | None:
        uid = uuid.UUID(str(account_id))
        query = select(Account).where(Account.id == uid, Account.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Account.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_accounts(self, filters: AccountListFilters) -> tuple[list[Account], int]:
        base = self._apply_list_filters(
            self._base_query(filters.organization_id),
            filters,
        )

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        nulls = (
            sort_column.nulls_last() if filters.sort_order == "desc" else sort_column.nulls_first()
        )

        result = await self._session.execute(
            base.order_by(nulls, order).offset(filters.skip).limit(filters.limit)
        )
        return list(result.scalars().all()), total

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Account], int]:
        filters = AccountListFilters(
            organization_id=organization_id,
            case_id=case_id,
            skip=skip,
            limit=limit,
        )
        return await self.list_accounts(filters)

    async def create(self, account: Account) -> Account:
        self._session.add(account)
        await self._session.flush()
        await self._session.refresh(account)
        return account

    async def update(self, account: Account) -> Account:
        await self._session.flush()
        await self._session.refresh(account)
        return account

    async def get_intelligence_summary(
        self,
        organization_id: uuid.UUID,
        *,
        case_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        base = self._base_query(organization_id)
        if case_id is not None:
            base = base.where(Account.case_id == case_id)
        subq = base.subquery()

        agg = await self._session.execute(
            select(
                func.count().label("total_accounts"),
                func.coalesce(func.sum(subq.c.balance), 0).label("total_balance"),
                func.coalesce(func.sum(subq.c.past_due_amount), 0).label("total_past_due"),
            ).select_from(subq)
        )
        totals = agg.one()

        collection_count = await self._count_where(
            organization_id, Account.account_status == AccountStatus.COLLECTION, case_id
        )
        charge_off_count = await self._count_where(
            organization_id,
            Account.account_status == AccountStatus.CHARGE_OFF,
            case_id,
        )
        critical_accounts = await self._count_where(
            organization_id,
            Account.risk_score >= CRITICAL_RISK_THRESHOLD,
            case_id,
        )
        dispute_ready_count = await self._count_where(
            organization_id,
            Account.dispute_status == DisputeStatus.READY_FOR_DISPUTE,
            case_id,
        )
        evidence_needed_count = await self._count_where(
            organization_id,
            Account.dispute_status == DisputeStatus.EVIDENCE_NEEDED,
            case_id,
        )

        accounts_by_bureau = await self._group_count(organization_id, Account.bureau, case_id)
        accounts_by_type = await self._group_count(organization_id, Account.account_type, case_id)
        accounts_by_status = await self._group_count(
            organization_id, Account.account_status, case_id
        )

        highest_balance = await self._top_accounts(
            organization_id,
            Account.balance.desc().nulls_last(),
            case_id,
            limit=5,
        )
        highest_risk = await self._top_accounts(
            organization_id,
            Account.risk_score.desc().nulls_last(),
            case_id,
            limit=5,
        )
        next_action = await self._top_accounts(
            organization_id,
            Account.readiness_score.desc().nulls_last(),
            case_id,
            limit=10,
        )

        return {
            "total_accounts": int(totals.total_accounts),
            "total_balance": Decimal(str(totals.total_balance)),
            "collection_count": collection_count,
            "charge_off_count": charge_off_count,
            "critical_accounts": critical_accounts,
            "dispute_ready_count": dispute_ready_count,
            "evidence_needed_count": evidence_needed_count,
            "total_past_due": Decimal(str(totals.total_past_due)),
            "accounts_by_bureau": accounts_by_bureau,
            "accounts_by_type": accounts_by_type,
            "accounts_by_status": accounts_by_status,
            "highest_balance_accounts": highest_balance,
            "highest_risk_accounts": highest_risk,
            "next_action_queue": next_action,
        }

    async def _count_where(
        self,
        organization_id: uuid.UUID,
        condition: Any,
        case_id: uuid.UUID | None,
    ) -> int:
        query = self._base_query(organization_id).where(condition)
        if case_id is not None:
            query = query.where(Account.case_id == case_id)
        result = await self._session.execute(select(func.count()).select_from(query.subquery()))
        return int(result.scalar_one())

    async def _group_count(
        self,
        organization_id: uuid.UUID,
        column: InstrumentedAttribute[Any],
        case_id: uuid.UUID | None,
    ) -> dict[str, int]:
        query = (
            select(column, func.count())
            .where(
                Account.organization_id == organization_id,
                Account.deleted_at.is_(None),
            )
            .group_by(column)
        )
        if case_id is not None:
            query = query.where(Account.case_id == case_id)
        result = await self._session.execute(query)
        return {str(row[0].value): int(row[1]) for row in result.all()}

    async def _top_accounts(
        self,
        organization_id: uuid.UUID,
        order: Any,
        case_id: uuid.UUID | None,
        *,
        limit: int,
    ) -> list[Account]:
        query = self._base_query(organization_id).order_by(order).limit(limit)
        if case_id is not None:
            query = query.where(Account.case_id == case_id)
        result = await self._session.execute(query)
        return list(result.scalars().all())
