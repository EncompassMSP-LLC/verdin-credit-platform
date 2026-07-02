"""Client portal read-only case progress endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.cases_service import ClientPortalCasesService
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalCaseDetailResponse,
    PortalCaseProgressResponse,
)

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_portal_cases_service(db: AsyncSession = Depends(get_db)) -> ClientPortalCasesService:
    return ClientPortalCasesService.from_session(db)


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
