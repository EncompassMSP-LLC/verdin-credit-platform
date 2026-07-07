"""Admin-gated multi-IdP bulk provisioning endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.bulk_idp_provisioning_dependencies import (
    require_bulk_idp_provisioning_enabled,
)
from api.modules.enterprise.bulk_idp_provisioning_schemas import (
    BulkIdpProvisioningRunListParams,
    BulkIdpProvisioningRunResponse,
    BulkIdpProvisioningRunResultResponse,
    BulkIdpProvisioningStatusResponse,
    BulkIdpProvisioningSubmitRequest,
)
from api.modules.enterprise.bulk_idp_provisioning_service import BulkIdpProvisioningService

bulk_idp_provisioning_router = APIRouter(
    prefix="/bulk-idp-provisioning",
    tags=["Multi-IdP Bulk Provisioning"],
)


def get_bulk_idp_provisioning_service(
    db: AsyncSession = Depends(get_db),
) -> BulkIdpProvisioningService:
    return BulkIdpProvisioningService.from_session(db)


@bulk_idp_provisioning_router.get("/status", response_model=BulkIdpProvisioningStatusResponse)
async def get_bulk_idp_provisioning_status_endpoint(
    _: None = Depends(require_bulk_idp_provisioning_enabled),
    service: BulkIdpProvisioningService = Depends(get_bulk_idp_provisioning_service),
) -> BulkIdpProvisioningStatusResponse:
    return service.get_status_response()


@bulk_idp_provisioning_router.get(
    "/runs",
    response_model=PaginatedResponse[BulkIdpProvisioningRunResponse],
)
async def list_bulk_idp_provisioning_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_bulk_idp_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: BulkIdpProvisioningService = Depends(get_bulk_idp_provisioning_service),
) -> PaginatedResponse[BulkIdpProvisioningRunResponse]:
    params = BulkIdpProvisioningRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@bulk_idp_provisioning_router.post(
    "/ui-runs/{hris_passwordless_ui_run_id}/start",
    response_model=BulkIdpProvisioningRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_bulk_idp_provisioning_run_endpoint(
    hris_passwordless_ui_run_id: uuid.UUID,
    body: BulkIdpProvisioningSubmitRequest,
    _: None = Depends(require_bulk_idp_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: BulkIdpProvisioningService = Depends(get_bulk_idp_provisioning_service),
) -> BulkIdpProvisioningRunResultResponse:
    return await service.submit_from_ui_run(current_user, hris_passwordless_ui_run_id, body)


@bulk_idp_provisioning_router.post(
    "/runs/{run_id}/approve",
    response_model=BulkIdpProvisioningRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_bulk_idp_provisioning_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_bulk_idp_provisioning_enabled),
    current_user: User = Depends(get_current_user),
    service: BulkIdpProvisioningService = Depends(get_bulk_idp_provisioning_service),
) -> BulkIdpProvisioningRunResultResponse:
    return await service.approve_run(current_user, run_id)
