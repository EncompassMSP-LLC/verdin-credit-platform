"""Repository for human-gated agent supervised loop runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_supervised_loop_models import (
    AgentSupervisedLoopRun,
    AgentSupervisedLoopStatus,
)


class AgentSupervisedLoopRunListFilters:
    def __init__(self, *, skip: int, limit: int, case_id: uuid.UUID | None = None) -> None:
        self.skip = skip
        self.limit = limit
        self.case_id = case_id


class AgentSupervisedLoopRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> AgentSupervisedLoopRun | None:
        result = await self._session.execute(
            select(AgentSupervisedLoopRun).where(AgentSupervisedLoopRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        tool_invocation_request_id: uuid.UUID,
        case_id: uuid.UUID | None,
        tool_kind: str,
        status: AgentSupervisedLoopStatus,
        loop_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> AgentSupervisedLoopRun:
        run = AgentSupervisedLoopRun(
            organization_id=organization_id,
            tool_invocation_request_id=tool_invocation_request_id,
            case_id=case_id,
            tool_kind=tool_kind,
            status=status,
            loop_summary=loop_summary,
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
        filters: AgentSupervisedLoopRunListFilters,
    ) -> tuple[list[AgentSupervisedLoopRun], int]:
        base = (
            select(AgentSupervisedLoopRun)
            .where(AgentSupervisedLoopRun.organization_id == organization_id)
            .order_by(AgentSupervisedLoopRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(AgentSupervisedLoopRun)
            .where(AgentSupervisedLoopRun.organization_id == organization_id)
        )
        if filters.case_id is not None:
            base = base.where(AgentSupervisedLoopRun.case_id == filters.case_id)
            count_query = count_query.where(AgentSupervisedLoopRun.case_id == filters.case_id)

        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
