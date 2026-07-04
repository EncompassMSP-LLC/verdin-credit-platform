"""Repository for agent observability runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_observability_models import (
    AgentObservabilityKind,
    AgentObservabilityRun,
    AgentObservabilityRunStatus,
    AgentObservabilityTriggerSource,
)


class AgentObservabilityRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class AgentObservabilityRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        agent_kind: AgentObservabilityKind,
        trigger_source: AgentObservabilityTriggerSource,
        status: AgentObservabilityRunStatus,
        performed_by_user_id: uuid.UUID | None,
        case_id: uuid.UUID | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        steps_completed: int = 0,
        steps_failed: int = 0,
        timeline_event_id: uuid.UUID | None = None,
        error_message: str | None = None,
    ) -> AgentObservabilityRun:
        run = AgentObservabilityRun(
            organization_id=organization_id,
            agent_kind=agent_kind,
            trigger_source=trigger_source,
            status=status,
            performed_by_user_id=performed_by_user_id,
            case_id=case_id,
            started_at=started_at,
            completed_at=completed_at,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            timeline_event_id=timeline_event_id,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: AgentObservabilityRunListFilters,
    ) -> tuple[list[AgentObservabilityRun], int]:
        base = (
            select(AgentObservabilityRun)
            .where(AgentObservabilityRun.organization_id == organization_id)
            .order_by(AgentObservabilityRun.started_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(AgentObservabilityRun)
            .where(AgentObservabilityRun.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
