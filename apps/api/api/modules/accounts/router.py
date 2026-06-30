"""Account management endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.models import (
    AccountBureau,
    AccountStatus,
    AccountType,
    DisputeStatus,
    PaymentStatus,
)
from api.modules.accounts.schemas import (
    AccountCreate,
    AccountIntelligenceSummary,
    AccountListParams,
    AccountResponse,
    AccountSortField,
    AccountSortOrder,
    AccountUpdate,
)
from api.modules.accounts.service import AccountService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

router = APIRouter(prefix="/accounts", tags=["Accounts"])


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService.from_session(db)


def get_account_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    case_id: uuid.UUID | None = None,
    bureau: AccountBureau | None = None,
    account_type: AccountType | None = None,
    account_status: AccountStatus | None = None,
    payment_status: PaymentStatus | None = None,
    dispute_status: DisputeStatus | None = None,
    min_risk_score: int | None = Query(None, ge=0, le=100),
    max_risk_score: int | None = Query(None, ge=0, le=100),
    min_readiness_score: int | None = Query(None, ge=0, le=100),
    dispute_ready: bool | None = None,
    sort_by: AccountSortField = "created_at",
    sort_order: AccountSortOrder = "desc",
) -> AccountListParams:
    return AccountListParams(
        page=page,
        page_size=page_size,
        search=search,
        case_id=case_id,
        bureau=bureau,
        account_type=account_type,
        account_status=account_status,
        payment_status=payment_status,
        dispute_status=dispute_status,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
        min_readiness_score=min_readiness_score,
        dispute_ready=dispute_ready,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    body: AccountCreate,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.create_account(current_user, body)


@router.get("/intelligence/summary", response_model=AccountIntelligenceSummary)
async def get_account_intelligence_summary(
    case_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountIntelligenceSummary:
    return await service.get_intelligence_summary(current_user, case_id=case_id)


@router.get("", response_model=PaginatedResponse[AccountResponse])
async def list_accounts(
    params: AccountListParams = Depends(get_account_list_params),
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> PaginatedResponse[AccountResponse]:
    return await service.list_accounts(current_user, params)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.get_account(current_user, account_id)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: uuid.UUID,
    body: AccountUpdate,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.update_account(current_user, account_id, body)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> None:
    await service.delete_account(current_user, account_id)
