"""Portal checklist / action-plan endpoints (LRP-104)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.checklist_service import ClientPortalChecklistService
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalChecklistItemResponse,
    PortalChecklistResponse,
    PortalChecklistUpdateRequest,
)

router = APIRouter(tags=["Client Portal"])


def get_portal_checklist_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalChecklistService:
    return ClientPortalChecklistService.from_session(db)


@router.get(
    "/portal/cases/{case_id}/checklist",
    response_model=PortalChecklistResponse,
)
async def list_portal_case_checklist(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalChecklistService = Depends(get_portal_checklist_service),
) -> PortalChecklistResponse:
    return await service.list_checklist(portal_user, case_id)


@router.patch(
    "/portal/checklist/{item_id}",
    response_model=PortalChecklistItemResponse,
)
async def update_portal_checklist_item(
    item_id: str,
    body: PortalChecklistUpdateRequest,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalChecklistService = Depends(get_portal_checklist_service),
) -> PortalChecklistItemResponse:
    return await service.update_item(portal_user, item_id, new_status=body.status)
