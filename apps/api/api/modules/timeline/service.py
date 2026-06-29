"""Timeline read service."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.timeline.permissions import TIMELINE_READ_ROLE
from api.modules.timeline.repository import TimelineListFilters, TimelineRepository
from api.modules.timeline.schemas import TimelineEventResponse, TimelineListParams


class TimelineService:
    def __init__(self, repo: TimelineRepository) -> None:
        self._timeline = repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> "TimelineService":
        return cls(TimelineRepository(session))

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, TIMELINE_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view timeline",
            )

    async def list_events(
        self,
        user: User,
        params: TimelineListParams,
    ) -> PaginatedResponse[TimelineEventResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        filters = TimelineListFilters(
            organization_id=organization_id,
            case_id=params.case_id,
            account_id=params.account_id,
            document_id=params.document_id,
            event_type=params.event_type,
            event_category=params.event_category,
            performed_by=params.performed_by,
            occurred_from=params.occurred_from,
            occurred_to=params.occurred_to,
            skip=params.offset,
            limit=params.limit,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        items, total = await self._timeline.list_events(filters)
        return paginate(
            [TimelineEventResponse.from_model(item) for item in items],
            total,
            params.page,
            params.page_size,
        )

    async def get_event(self, user: User, event_id: uuid.UUID) -> TimelineEventResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        event = await self._timeline.get_by_id(event_id, organization_id=organization_id)
        if event is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return TimelineEventResponse.from_model(event)
