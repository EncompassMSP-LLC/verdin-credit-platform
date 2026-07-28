"""Client portal read-only case progress endpoints."""

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.accounts.credit_analysis_schemas import PortalCaseReadinessResponse
from api.modules.client_portal.cases_service import ClientPortalCasesService
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.dispute_strategy_service import ClientPortalDisputeStrategyService
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalCaseDetailResponse,
    PortalCaseProgressResponse,
    PortalDisputeStrategySuggestionsResponse,
    PortalReadinessReportResponse,
    PortalTimelineResponse,
)
from api.modules.client_portal.timeline_service import ClientPortalTimelineService

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_portal_cases_service(db: AsyncSession = Depends(get_db)) -> ClientPortalCasesService:
    return ClientPortalCasesService.from_session(db)


def get_portal_timeline_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalTimelineService:
    return ClientPortalTimelineService.from_session(db)


def get_portal_dispute_strategy_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalDisputeStrategyService:
    return ClientPortalDisputeStrategyService.from_session(db)


@router.get("", response_model=PortalCaseProgressResponse)
async def list_portal_cases(
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalCasesService = Depends(get_portal_cases_service),
) -> PortalCaseProgressResponse:
    return await service.list_cases(portal_user)


@router.get("/{case_id}", response_model=PortalCaseDetailResponse)
async def get_portal_case(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalCasesService = Depends(get_portal_cases_service),
) -> PortalCaseDetailResponse:
    return await service.get_case(portal_user, case_id)


@router.get("/{case_id}/readiness", response_model=PortalCaseReadinessResponse)
async def get_portal_case_readiness(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalCasesService = Depends(get_portal_cases_service),
) -> PortalCaseReadinessResponse:
    return await service.get_case_readiness(portal_user, case_id)


@router.get("/{case_id}/timeline", response_model=PortalTimelineResponse)
async def get_portal_case_timeline(
    case_id: uuid.UUID,
    event_type: str | None = Query(default=None),
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalTimelineService = Depends(get_portal_timeline_service),
) -> PortalTimelineResponse:
    return await service.list_timeline(portal_user, case_id, event_type=event_type)


@router.get(
    "/{case_id}/dispute-strategy-suggestions",
    response_model=PortalDisputeStrategySuggestionsResponse,
)
async def get_portal_dispute_strategy_suggestions(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalDisputeStrategyService = Depends(get_portal_dispute_strategy_service),
) -> PortalDisputeStrategySuggestionsResponse:
    """Advisory dispute strategy suggestions for the borrower (LRP-403).

    Read-only projection of the latest staff strategy run. Never prepares or sends.
    """
    return await service.get_suggestions(portal_user, case_id)


@router.get("/{case_id}/readiness-report", response_model=PortalReadinessReportResponse)
async def get_portal_case_readiness_report(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalCasesService = Depends(get_portal_cases_service),
) -> PortalReadinessReportResponse:
    return await service.get_case_readiness_report(portal_user, case_id)


@router.get("/{case_id}/readiness-report/export")
async def export_portal_case_readiness_report(
    case_id: uuid.UUID,
    format: Literal["text", "pdf"] = Query(default="pdf", alias="format"),
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalCasesService = Depends(get_portal_cases_service),
) -> Response:
    content, media_type, filename = await service.export_case_readiness_report(
        portal_user,
        case_id,
        export_format=format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
