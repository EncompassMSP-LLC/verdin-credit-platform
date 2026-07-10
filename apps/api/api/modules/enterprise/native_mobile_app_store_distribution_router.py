"""Admin-gated native mobile app store distribution endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.native_mobile_app_store_distribution_dependencies import (
    require_native_mobile_app_store_distribution_enabled,
)
from api.modules.enterprise.native_mobile_app_store_distribution_schemas import (
    NativeMobileAppStoreDistributionRunListParams,
    NativeMobileAppStoreDistributionRunResponse,
    NativeMobileAppStoreDistributionRunResultResponse,
    NativeMobileAppStoreDistributionStatusResponse,
    NativeMobileAppStoreDistributionSubmitRequest,
)
from api.modules.enterprise.native_mobile_app_store_distribution_service import (
    NativeMobileAppStoreDistributionService,
)

native_mobile_app_store_distribution_router = APIRouter(
    prefix="/native-mobile-app-store-distribution",
    tags=["Native Mobile App Store Distribution"],
)


def get_native_mobile_app_store_distribution_service(
    db: AsyncSession = Depends(get_db),
) -> NativeMobileAppStoreDistributionService:
    return NativeMobileAppStoreDistributionService.from_session(db)


@native_mobile_app_store_distribution_router.get(
    "/status",
    response_model=NativeMobileAppStoreDistributionStatusResponse,
)
async def get_native_mobile_app_store_distribution_status_endpoint(
    _: None = Depends(require_native_mobile_app_store_distribution_enabled),
    service: NativeMobileAppStoreDistributionService = Depends(
        get_native_mobile_app_store_distribution_service
    ),
) -> NativeMobileAppStoreDistributionStatusResponse:
    return service.get_status_response()


@native_mobile_app_store_distribution_router.get(
    "/runs",
    response_model=PaginatedResponse[NativeMobileAppStoreDistributionRunResponse],
)
async def list_native_mobile_app_store_distribution_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_native_mobile_app_store_distribution_enabled),
    current_user: User = Depends(get_current_user),
    service: NativeMobileAppStoreDistributionService = Depends(
        get_native_mobile_app_store_distribution_service
    ),
) -> PaginatedResponse[NativeMobileAppStoreDistributionRunResponse]:
    params = NativeMobileAppStoreDistributionRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@native_mobile_app_store_distribution_router.post(
    "/passkey-client-runs/{native_mobile_passkey_client_run_id}/start",
    response_model=NativeMobileAppStoreDistributionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_native_mobile_app_store_distribution_run_endpoint(
    native_mobile_passkey_client_run_id: uuid.UUID,
    body: NativeMobileAppStoreDistributionSubmitRequest,
    _: None = Depends(require_native_mobile_app_store_distribution_enabled),
    current_user: User = Depends(get_current_user),
    service: NativeMobileAppStoreDistributionService = Depends(
        get_native_mobile_app_store_distribution_service
    ),
) -> NativeMobileAppStoreDistributionRunResultResponse:
    return await service.submit_from_passkey_client_run(
        current_user, native_mobile_passkey_client_run_id, body
    )


@native_mobile_app_store_distribution_router.post(
    "/runs/{run_id}/approve",
    response_model=NativeMobileAppStoreDistributionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_native_mobile_app_store_distribution_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_native_mobile_app_store_distribution_enabled),
    current_user: User = Depends(get_current_user),
    service: NativeMobileAppStoreDistributionService = Depends(
        get_native_mobile_app_store_distribution_service
    ),
) -> NativeMobileAppStoreDistributionRunResultResponse:
    return await service.approve_run(current_user, run_id)
