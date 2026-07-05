"""Repository for human-gated agent external tool invocation requests."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.llm.agent_tool_calling_models import (
    AgentExternalToolKind,
    AgentToolInvocationRequest,
    AgentToolInvocationStatus,
)


class AgentToolInvocationRequestListFilters:
    def __init__(self, *, skip: int, limit: int, case_id: uuid.UUID | None = None) -> None:
        self.skip = skip
        self.limit = limit
        self.case_id = case_id


class AgentToolInvocationRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_request_by_id(self, request_id: uuid.UUID) -> AgentToolInvocationRequest | None:
        result = await self._session.execute(
            select(AgentToolInvocationRequest).where(AgentToolInvocationRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def create_request(
        self,
        *,
        organization_id: uuid.UUID,
        tool_kind: AgentExternalToolKind,
        status: AgentToolInvocationStatus,
        invocation_summary: str,
        requested_by_user_id: uuid.UUID | None,
        case_id: uuid.UUID | None = None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> AgentToolInvocationRequest:
        request = AgentToolInvocationRequest(
            organization_id=organization_id,
            tool_kind=tool_kind,
            status=status,
            case_id=case_id,
            invocation_summary=invocation_summary,
            requested_by_user_id=requested_by_user_id,
            requested_at=requested_at,
            error_message=error_message,
        )
        self._session.add(request)
        await self._session.flush()
        await self._session.refresh(request)
        return request

    async def list_requests(
        self,
        organization_id: uuid.UUID,
        filters: AgentToolInvocationRequestListFilters,
    ) -> tuple[list[AgentToolInvocationRequest], int]:
        base = (
            select(AgentToolInvocationRequest)
            .where(AgentToolInvocationRequest.organization_id == organization_id)
            .order_by(AgentToolInvocationRequest.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(AgentToolInvocationRequest)
            .where(AgentToolInvocationRequest.organization_id == organization_id)
        )
        if filters.case_id is not None:
            base = base.where(AgentToolInvocationRequest.case_id == filters.case_id)
            count_query = count_query.where(AgentToolInvocationRequest.case_id == filters.case_id)

        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
