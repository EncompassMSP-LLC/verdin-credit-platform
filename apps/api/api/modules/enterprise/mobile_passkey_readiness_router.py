"""Admin-gated mobile passkey readiness endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.mobile_passkey_readiness_dependencies import (
    require_mobile_passkey_readiness_enabled,
)
from api.modules.enterprise.mobile_passkey_readiness_schemas import (
    MobilePasskeyReadinessRunListParams,
    MobilePasskeyReadinessRunResponse,
    MobilePasskeyReadinessRunResultResponse,
    MobilePasskeyReadinessStatusResponse,
    MobilePasskeyReadinessSubmitRequest,
)
from api.modules.enterprise.mobile_passkey_readiness_service import MobilePasskeyReadinessService

mobile_passkey_readiness_router = APIRouter(
    prefix="/mobile-passkey-readiness",
    tags=["Mobile Passkey Readiness"],
)


def get_mobile_passkey_readiness_service(
    db: AsyncSession = Depends(get_db),
) -> MobilePasskeyReadinessService:
    return MobilePasskeyReadinessService.from_session(db)


@mobile_passkey_readiness_router.get("/status", response_model=MobilePasskeyReadinessStatusResponse)
async def get_mobile_passkey_readiness_status_endpoint(
    _: None = Depends(require_mobile_passkey_readiness_enabled),
    service: MobilePasskeyReadinessService = Depends(get_mobile_passkey_readiness_service),
) -> MobilePasskeyReadinessStatusResponse:
    return service.get_status_response()


@mobile_passkey_readiness_router.get(
    "/runs",
    response_model=PaginatedResponse[MobilePasskeyReadinessRunResponse],
)
async def list_mobile_passkey_readiness_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_mobile_passkey_readiness_enabled),
    current_user: User = Depends(get_current_user),
    service: MobilePasskeyReadinessService = Depends(get_mobile_passkey_readiness_service),
) -> PaginatedResponse[MobilePasskeyReadinessRunResponse]:
    params = MobilePasskeyReadinessRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@mobile_passkey_readiness_router.post(
    "/ui-runs/{hris_passwordless_ui_run_id}/start",
    response_model=MobilePasskeyReadinessRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_mobile_passkey_readiness_run_endpoint(
    hris_passwordless_ui_run_id: uuid.UUID,
    body: MobilePasskeyReadinessSubmitRequest,
    _: None = Depends(require_mobile_passkey_readiness_enabled),
    current_user: User = Depends(get_current_user),
    service: MobilePasskeyReadinessService = Depends(get_mobile_passkey_readiness_service),
) -> MobilePasskeyReadinessRunResultResponse:
    return await service.submit_from_ui_run(current_user, hris_passwordless_ui_run_id, body)


@mobile_passkey_readiness_router.post(
    "/runs/{run_id}/approve",
    response_model=MobilePasskeyReadinessRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_mobile_passkey_readiness_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_mobile_passkey_readiness_enabled),
    current_user: User = Depends(get_current_user),
    service: MobilePasskeyReadinessService = Depends(get_mobile_passkey_readiness_service),
) -> MobilePasskeyReadinessRunResultResponse:
    return await service.approve_run(current_user, run_id)
