"""Repository for human-gated agent execution steps."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_execution_models import (
    AgentExecutionStep,
    AgentExecutionStepStatus,
)
from api.modules.llm.agent_observability_models import AgentObservabilityKind


class AgentExecutionStepListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class AgentExecutionStepRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_step_by_id(self, step_id: uuid.UUID) -> AgentExecutionStep | None:
        result = await self._session.execute(
            select(AgentExecutionStep).where(AgentExecutionStep.id == step_id)
        )
        return result.scalar_one_or_none()

    async def create_step(
        self,
        *,
        organization_id: uuid.UUID,
        agent_kind: AgentObservabilityKind,
        status: AgentExecutionStepStatus,
        step_summary: str,
        requested_by_user_id: uuid.UUID | None,
        case_id: uuid.UUID | None = None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> AgentExecutionStep:
        step = AgentExecutionStep(
            organization_id=organization_id,
            agent_kind=agent_kind,
            status=status,
            step_summary=step_summary,
            requested_by_user_id=requested_by_user_id,
            case_id=case_id,
            requested_at=requested_at,
            error_message=error_message,
        )
        self._session.add(step)
        await self._session.flush()
        await self._session.refresh(step)
        return step

    async def list_steps(
        self,
        organization_id: uuid.UUID,
        filters: AgentExecutionStepListFilters,
    ) -> tuple[list[AgentExecutionStep], int]:
        base = (
            select(AgentExecutionStep)
            .where(AgentExecutionStep.organization_id == organization_id)
            .order_by(AgentExecutionStep.requested_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(AgentExecutionStep)
            .where(AgentExecutionStep.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
