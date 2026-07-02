"""Case management endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.schemas import (
    AccountListParams,
    AccountResponse,
    AccountSortField,
    AccountSortOrder,
)
from api.modules.accounts.service import AccountService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.cases.llm_summary import CaseLlmSummaryService
from api.modules.cases.models import CasePriority, CaseStage, CaseStatus
from api.modules.cases.schemas import (
    CaseCreate,
    CaseListParams,
    CaseLlmSummaryResponse,
    CaseResponse,
    CaseSortField,
    CaseSortOrder,
    CaseUpdate,
)
from api.modules.cases.service import CaseService

router = APIRouter(prefix="/cases", tags=["Cases"])


def get_case_service(db: AsyncSession = Depends(get_db)) -> CaseService:
    return CaseService.from_session(db)


def get_case_llm_summary_service(db: AsyncSession = Depends(get_db)) -> CaseLlmSummaryService:
    return CaseLlmSummaryService.from_session(db)


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService.from_session(db)


def get_case_account_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: AccountSortField = "created_at",
    sort_order: AccountSortOrder = "desc",
) -> AccountListParams:
    return AccountListParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def get_case_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    status: CaseStatus | None = None,
    stage: CaseStage | None = None,
    priority: CasePriority | None = None,
    assigned_user_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    sort_by: CaseSortField = "created_at",
    sort_order: CaseSortOrder = "desc",
) -> CaseListParams:
    return CaseListParams(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        stage=stage,
        priority=priority,
        assigned_user_id=assigned_user_id,
        client_id=client_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    body: CaseCreate,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    return await service.create_case(current_user, body)


@router.get("", response_model=PaginatedResponse[CaseResponse])
async def list_cases(
    params: CaseListParams = Depends(get_case_list_params),
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> PaginatedResponse[CaseResponse]:
    return await service.list_cases(current_user, params)


@router.post("/{case_id}/llm-summary", response_model=CaseLlmSummaryResponse)
async def generate_case_llm_summary(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CaseLlmSummaryService = Depends(get_case_llm_summary_service),
) -> CaseLlmSummaryResponse:
    return await service.generate_summary(current_user, case_id)


@router.get("/{case_id}/accounts", response_model=PaginatedResponse[AccountResponse])
async def list_case_accounts(
    case_id: uuid.UUID,
    params: AccountListParams = Depends(get_case_account_list_params),
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> PaginatedResponse[AccountResponse]:
    return await service.list_case_accounts(current_user, case_id, params)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    return await service.get_case(current_user, case_id)


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    body: CaseUpdate,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    return await service.update_case(current_user, case_id, body)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> None:
    await service.delete_case(current_user, case_id)
