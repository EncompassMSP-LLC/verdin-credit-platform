"""Admin-gated HRIS passwordless UI endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.hris_passwordless_ui_dependencies import (
    require_hris_passwordless_ui_enabled,
)
from api.modules.enterprise.hris_passwordless_ui_schemas import (
    HrisPasswordlessUiRunListParams,
    HrisPasswordlessUiRunResponse,
    HrisPasswordlessUiRunResultResponse,
    HrisPasswordlessUiStatusResponse,
    HrisPasswordlessUiSubmitRequest,
)
from api.modules.enterprise.hris_passwordless_ui_service import HrisPasswordlessUiService

hris_passwordless_ui_router = APIRouter(
    prefix="/hris-passwordless-ui",
    tags=["HRIS Passwordless UI"],
)


def get_hris_passwordless_ui_service(
    db: AsyncSession = Depends(get_db),
) -> HrisPasswordlessUiService:
    return HrisPasswordlessUiService.from_session(db)


@hris_passwordless_ui_router.get("/status", response_model=HrisPasswordlessUiStatusResponse)
async def get_hris_passwordless_ui_status_endpoint(
    _: None = Depends(require_hris_passwordless_ui_enabled),
    service: HrisPasswordlessUiService = Depends(get_hris_passwordless_ui_service),
) -> HrisPasswordlessUiStatusResponse:
    return service.get_status_response()


@hris_passwordless_ui_router.get(
    "/runs",
    response_model=PaginatedResponse[HrisPasswordlessUiRunResponse],
)
async def list_hris_passwordless_ui_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_hris_passwordless_ui_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisPasswordlessUiService = Depends(get_hris_passwordless_ui_service),
) -> PaginatedResponse[HrisPasswordlessUiRunResponse]:
    params = HrisPasswordlessUiRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@hris_passwordless_ui_router.post(
    "/enrollment-runs/{saml_passwordless_enrollment_run_id}/start",
    response_model=HrisPasswordlessUiRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_hris_passwordless_ui_run_endpoint(
    saml_passwordless_enrollment_run_id: uuid.UUID,
    body: HrisPasswordlessUiSubmitRequest,
    _: None = Depends(require_hris_passwordless_ui_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisPasswordlessUiService = Depends(get_hris_passwordless_ui_service),
) -> HrisPasswordlessUiRunResultResponse:
    return await service.submit_from_enrollment_run(
        current_user, saml_passwordless_enrollment_run_id, body
    )


@hris_passwordless_ui_router.post(
    "/runs/{run_id}/approve",
    response_model=HrisPasswordlessUiRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_hris_passwordless_ui_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_hris_passwordless_ui_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisPasswordlessUiService = Depends(get_hris_passwordless_ui_service),
) -> HrisPasswordlessUiRunResultResponse:
    return await service.approve_run(current_user, run_id)
