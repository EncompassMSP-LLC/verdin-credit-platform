"""Admin-gated native mobile passkey client endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.native_mobile_passkey_client_dependencies import (
    require_native_mobile_passkey_client_enabled,
)
from api.modules.enterprise.native_mobile_passkey_client_schemas import (
    NativeMobilePasskeyClientRunListParams,
    NativeMobilePasskeyClientRunResponse,
    NativeMobilePasskeyClientRunResultResponse,
    NativeMobilePasskeyClientStatusResponse,
    NativeMobilePasskeyClientSubmitRequest,
)
from api.modules.enterprise.native_mobile_passkey_client_service import (
    NativeMobilePasskeyClientService,
)

native_mobile_passkey_client_router = APIRouter(
    prefix="/native-mobile-passkey-client",
    tags=["Native Mobile Passkey Client"],
)


def get_native_mobile_passkey_client_service(
    db: AsyncSession = Depends(get_db),
) -> NativeMobilePasskeyClientService:
    return NativeMobilePasskeyClientService.from_session(db)


@native_mobile_passkey_client_router.get(
    "/status",
    response_model=NativeMobilePasskeyClientStatusResponse,
)
async def get_native_mobile_passkey_client_status_endpoint(
    _: None = Depends(require_native_mobile_passkey_client_enabled),
    service: NativeMobilePasskeyClientService = Depends(get_native_mobile_passkey_client_service),
) -> NativeMobilePasskeyClientStatusResponse:
    return service.get_status_response()


@native_mobile_passkey_client_router.get(
    "/runs",
    response_model=PaginatedResponse[NativeMobilePasskeyClientRunResponse],
)
async def list_native_mobile_passkey_client_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_native_mobile_passkey_client_enabled),
    current_user: User = Depends(get_current_user),
    service: NativeMobilePasskeyClientService = Depends(get_native_mobile_passkey_client_service),
) -> PaginatedResponse[NativeMobilePasskeyClientRunResponse]:
    params = NativeMobilePasskeyClientRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@native_mobile_passkey_client_router.post(
    "/readiness-runs/{mobile_passkey_readiness_run_id}/start",
    response_model=NativeMobilePasskeyClientRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_native_mobile_passkey_client_run_endpoint(
    mobile_passkey_readiness_run_id: uuid.UUID,
    body: NativeMobilePasskeyClientSubmitRequest,
    _: None = Depends(require_native_mobile_passkey_client_enabled),
    current_user: User = Depends(get_current_user),
    service: NativeMobilePasskeyClientService = Depends(get_native_mobile_passkey_client_service),
) -> NativeMobilePasskeyClientRunResultResponse:
    return await service.submit_from_readiness_run(
        current_user, mobile_passkey_readiness_run_id, body
    )


@native_mobile_passkey_client_router.post(
    "/runs/{run_id}/approve",
    response_model=NativeMobilePasskeyClientRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_native_mobile_passkey_client_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_native_mobile_passkey_client_enabled),
    current_user: User = Depends(get_current_user),
    service: NativeMobilePasskeyClientService = Depends(get_native_mobile_passkey_client_service),
) -> NativeMobilePasskeyClientRunResultResponse:
    return await service.approve_run(current_user, run_id)
