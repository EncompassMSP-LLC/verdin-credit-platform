"""Timeline and audit endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.timeline.schemas import (
    TimelineEventResponse,
    TimelineListParams,
    TimelineSortField,
    TimelineSortOrder,
)
from api.modules.timeline.service import TimelineService

router = APIRouter(prefix="/timeline", tags=["Timeline"])


def get_timeline_service(db: AsyncSession = Depends(get_db)) -> TimelineService:
    return TimelineService.from_session(db)


def get_timeline_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    document_id: uuid.UUID | None = None,
    event_type: str | None = None,
    event_category: str | None = None,
    performed_by: uuid.UUID | None = None,
    occurred_from: datetime | None = None,
    occurred_to: datetime | None = None,
    sort_by: TimelineSortField = "occurred_at",
    sort_order: TimelineSortOrder = "desc",
) -> TimelineListParams:
    return TimelineListParams(
        page=page,
        page_size=page_size,
        case_id=case_id,
        account_id=account_id,
        document_id=document_id,
        event_type=event_type,
        event_category=event_category,
        performed_by=performed_by,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("", response_model=PaginatedResponse[TimelineEventResponse])
async def list_timeline_events(
    params: TimelineListParams = Depends(get_timeline_list_params),
    current_user: User = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service),
) -> PaginatedResponse[TimelineEventResponse]:
    return await service.list_events(current_user, params)


@router.get("/{event_id}", response_model=TimelineEventResponse)
async def get_timeline_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineEventResponse:
    return await service.get_event(current_user, event_id)
