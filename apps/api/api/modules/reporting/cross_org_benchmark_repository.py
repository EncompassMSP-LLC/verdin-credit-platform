"""Cross-org benchmark analytics repository."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.models import Account, DisputeStatus
from api.modules.cases.models import Case, CaseStatus
from api.modules.clients.models import Client, ClientStatus
from api.modules.reporting.cross_org_benchmark_models import (
    CrossOrgBenchmarkRun,
    CrossOrgBenchmarkRunStatus,
    CrossOrgBenchmarkTriggerSource,
)


@dataclass
class CrossOrgBenchmarkSummary:
    organization_id: uuid.UUID
    active_clients: int
    open_cases: int
    resolved_accounts: int
    cohort_average_active_clients: float
    cohort_average_open_cases: float
    cohort_average_resolved_accounts: float
    active_clients_percentile: int
    open_cases_percentile: int
    resolved_accounts_percentile: int
    organizations_evaluated: int


class CrossOrgBenchmarkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _active_clients_by_org(self) -> dict[uuid.UUID, int]:
        rows = await self._session.execute(
            select(Client.organization_id, func.count())
            .where(
                Client.deleted_at.is_(None),
                Client.status == ClientStatus.ACTIVE,
            )
            .group_by(Client.organization_id)
        )
        return {org_id: int(count) for org_id, count in rows.all() if org_id is not None}

    async def _open_cases_by_org(self) -> dict[uuid.UUID, int]:
        rows = await self._session.execute(
            select(Case.organization_id, func.count())
            .where(
                Case.deleted_at.is_(None),
                Case.status.not_in([CaseStatus.CLOSED, CaseStatus.RESOLVED]),
            )
            .group_by(Case.organization_id)
        )
        return {org_id: int(count) for org_id, count in rows.all() if org_id is not None}

    async def _resolved_accounts_by_org(self) -> dict[uuid.UUID, int]:
        rows = await self._session.execute(
            select(Account.organization_id, func.count())
            .where(
                Account.deleted_at.is_(None),
                Account.dispute_status.in_(
                    [DisputeStatus.CORRECTED, DisputeStatus.DELETED, DisputeStatus.VERIFIED]
                ),
            )
            .group_by(Account.organization_id)
        )
        return {org_id: int(count) for org_id, count in rows.all() if org_id is not None}

    async def build_summary(self, organization_id: uuid.UUID) -> CrossOrgBenchmarkSummary:
        active_clients = await self._active_clients_by_org()
        open_cases = await self._open_cases_by_org()
        resolved_accounts = await self._resolved_accounts_by_org()

        org_ids = set(active_clients) | set(open_cases) | set(resolved_accounts) | {organization_id}
        org_rows = [
            (
                org_id,
                active_clients.get(org_id, 0),
                open_cases.get(org_id, 0),
                resolved_accounts.get(org_id, 0),
            )
            for org_id in org_ids
        ]

        org_count = len(org_rows)
        avg_active_clients = sum(row[1] for row in org_rows) / org_count if org_count else 0.0
        avg_open_cases = sum(row[2] for row in org_rows) / org_count if org_count else 0.0
        avg_resolved_accounts = sum(row[3] for row in org_rows) / org_count if org_count else 0.0

        def percentile(target: int, values: list[int]) -> int:
            if not values:
                return 0
            below_or_equal = sum(1 for value in values if value <= target)
            return round((below_or_equal / len(values)) * 100)

        active_values = [row[1] for row in org_rows]
        open_case_values = [row[2] for row in org_rows]
        resolved_values = [row[3] for row in org_rows]

        return CrossOrgBenchmarkSummary(
            organization_id=organization_id,
            active_clients=active_clients.get(organization_id, 0),
            open_cases=open_cases.get(organization_id, 0),
            resolved_accounts=resolved_accounts.get(organization_id, 0),
            cohort_average_active_clients=round(avg_active_clients, 2),
            cohort_average_open_cases=round(avg_open_cases, 2),
            cohort_average_resolved_accounts=round(avg_resolved_accounts, 2),
            active_clients_percentile=percentile(
                active_clients.get(organization_id, 0), active_values
            ),
            open_cases_percentile=percentile(open_cases.get(organization_id, 0), open_case_values),
            resolved_accounts_percentile=percentile(
                resolved_accounts.get(organization_id, 0), resolved_values
            ),
            organizations_evaluated=org_count,
        )

    async def create_run(
        self,
        *,
        requested_by_id: uuid.UUID,
        organizations_evaluated: int,
        status: CrossOrgBenchmarkRunStatus = CrossOrgBenchmarkRunStatus.COMPLETED,
        error_message: str | None = None,
    ) -> CrossOrgBenchmarkRun:
        run = CrossOrgBenchmarkRun(
            requested_by_id=requested_by_id,
            trigger_source=CrossOrgBenchmarkTriggerSource.MANUAL,
            status=status,
            organizations_evaluated=organizations_evaluated,
            generated_at=datetime.now(UTC),
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(self, *, limit: int = 20) -> list[CrossOrgBenchmarkRun]:
        result = await self._session.execute(
            select(CrossOrgBenchmarkRun)
            .order_by(CrossOrgBenchmarkRun.generated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
