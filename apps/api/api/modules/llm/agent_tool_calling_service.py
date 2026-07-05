"""Human-gated agent external tool invocation service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.agent_external_tool_calling import get_agent_external_tool_calling_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.permissions import CASE_READ_ROLE, CASE_WRITE_ROLE
from api.modules.llm.agent_tool_calling_models import AgentToolInvocationStatus
from api.modules.llm.agent_tool_calling_processor import (
    approve_agent_tool_invocation_request,
    submit_agent_tool_invocation_request,
)
from api.modules.llm.agent_tool_calling_repository import (
    AgentToolInvocationRequestListFilters,
    AgentToolInvocationRequestRepository,
)
from api.modules.llm.agent_tool_calling_schemas import (
    AgentExternalToolCallingStatusResponse,
    AgentToolInvocationRequestListParams,
    AgentToolInvocationRequestResponse,
    AgentToolInvocationRequestResultResponse,
    AgentToolInvocationSubmitRequest,
)


class AgentToolCallingService:
    def __init__(
        self,
        request_repo: AgentToolInvocationRequestRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._requests = request_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> AgentToolCallingService:
        return cls(AgentToolInvocationRequestRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, CASE_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view agent tool invocation requests",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit agent tool invocation requests",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve agent tool invocation requests",
            )

    def _require_ready(self) -> None:
        tool_status = get_agent_external_tool_calling_status()
        if not tool_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Agent external tool calling is not ready",
                    "blockers": list(tool_status.blockers),
                },
            )

    def get_status_response(self) -> AgentExternalToolCallingStatusResponse:
        return AgentExternalToolCallingStatusResponse.from_status(
            get_agent_external_tool_calling_status()
        )

    async def list_requests(
        self,
        user: User,
        params: AgentToolInvocationRequestListParams,
    ) -> PaginatedResponse[AgentToolInvocationRequestResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        requests, total = await self._requests.list_requests(
            organization_id,
            AgentToolInvocationRequestListFilters(
                skip=skip,
                limit=params.page_size,
                case_id=params.case_id,
            ),
        )
        items = [AgentToolInvocationRequestResponse.from_model(item) for item in requests]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_request(
        self,
        user: User,
        body: AgentToolInvocationSubmitRequest,
    ) -> AgentToolInvocationRequestResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        summary = await submit_agent_tool_invocation_request(
            session=self._session,
            organization_id=organization_id,
            tool_kind=body.tool_kind,
            invocation_summary=body.invocation_summary,
            requested_by_user_id=user.id,
            case_id=body.case_id,
        )
        if summary.request.status == AgentToolInvocationStatus.FAILED:
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary.request.error_message or "Agent tool invocation request failed",
            )
        await self._session.commit()
        return AgentToolInvocationRequestResultResponse(
            completed_at=summary.completed_at,
            request=AgentToolInvocationRequestResponse.from_model(summary.request),
        )

    async def approve_request(
        self,
        user: User,
        request_id: uuid.UUID,
    ) -> AgentToolInvocationRequestResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_agent_tool_invocation_request(
                session=self._session,
                organization_id=organization_id,
                request_id=request_id,
                approved_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT
                if "not pending approval" in detail
                else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return AgentToolInvocationRequestResultResponse(
            completed_at=summary.completed_at,
            request=AgentToolInvocationRequestResponse.from_model(summary.request),
        )
