"""Repository for admin-gated agent arbitrary execution runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_arbitrary_execution_models import (
    AgentArbitraryExecutionRun,
    AgentArbitraryExecutionRunStatus,
)


class AgentArbitraryExecutionRunListFilters:
    def __init__(self, *, skip: int, limit: int, case_id: uuid.UUID | None = None) -> None:
        self.skip = skip
        self.limit = limit
        self.case_id = case_id


class AgentArbitraryExecutionRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> AgentArbitraryExecutionRun | None:
        result = await self._session.execute(
            select(AgentArbitraryExecutionRun).where(AgentArbitraryExecutionRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        agent_unsupervised_loop_run_id: uuid.UUID,
        case_id: uuid.UUID | None,
        tool_kind: str,
        status: AgentArbitraryExecutionRunStatus,
        execution_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> AgentArbitraryExecutionRun:
        run = AgentArbitraryExecutionRun(
            organization_id=organization_id,
            agent_unsupervised_loop_run_id=agent_unsupervised_loop_run_id,
            case_id=case_id,
            tool_kind=tool_kind,
            status=status,
            execution_summary=execution_summary,
            requested_by_user_id=requested_by_user_id,
            requested_at=requested_at,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: AgentArbitraryExecutionRunListFilters,
    ) -> tuple[list[AgentArbitraryExecutionRun], int]:
        base = (
            select(AgentArbitraryExecutionRun)
            .where(AgentArbitraryExecutionRun.organization_id == organization_id)
            .order_by(AgentArbitraryExecutionRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(AgentArbitraryExecutionRun)
            .where(AgentArbitraryExecutionRun.organization_id == organization_id)
        )
        if filters.case_id is not None:
            base = base.where(AgentArbitraryExecutionRun.case_id == filters.case_id)
            count_query = count_query.where(AgentArbitraryExecutionRun.case_id == filters.case_id)

        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
