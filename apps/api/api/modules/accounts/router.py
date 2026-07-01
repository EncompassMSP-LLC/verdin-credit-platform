"""Account management endpoints."""

import uuid
from typing import Literal

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
    AccountDisputeDraftResponse,
    AccountDisputeResponseReceivedRequest,
    AccountIntelligenceSummary,
    AccountListParams,
    AccountResponse,
    AccountSortField,
    AccountSortOrder,
    AccountUpdate,
    DisputeLetterResponse,
)
from api.modules.accounts.service import AccountService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.tasks.schemas import TaskResponse

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


@router.get("/{account_id}/dispute-draft", response_model=AccountDisputeDraftResponse)
async def get_account_dispute_draft(
    account_id: uuid.UUID,
    recipient_type: Literal["credit_bureau", "furnisher"] = Query(default="credit_bureau"),
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountDisputeDraftResponse:
    return await service.get_dispute_draft(
        current_user,
        account_id,
        recipient_type=recipient_type,
    )


@router.post("/{account_id}/dispute-draft/review-task", response_model=TaskResponse)
async def create_account_dispute_draft_review_task(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> TaskResponse:
    return await service.create_dispute_draft_review_task(current_user, account_id)


@router.post("/{account_id}/dispute-draft/letters", response_model=DisputeLetterResponse)
async def create_account_dispute_letter_draft(
    account_id: uuid.UUID,
    recipient_type: Literal["credit_bureau", "furnisher"] = Query(default="credit_bureau"),
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> DisputeLetterResponse:
    return await service.create_dispute_letter_draft(
        current_user,
        account_id,
        recipient_type=recipient_type,
    )


@router.get("/{account_id}/dispute-letters", response_model=list[DisputeLetterResponse])
async def list_account_dispute_letters(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> list[DisputeLetterResponse]:
    return await service.list_dispute_letters(current_user, account_id)


@router.get(
    "/{account_id}/dispute-letters/{letter_id}",
    response_model=DisputeLetterResponse,
)
async def get_account_dispute_letter(
    account_id: uuid.UUID,
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> DisputeLetterResponse:
    return await service.get_dispute_letter(current_user, account_id, letter_id)


@router.post(
    "/{account_id}/dispute-letters/{letter_id}/review-task",
    response_model=TaskResponse,
)
async def create_account_dispute_letter_review_task(
    account_id: uuid.UUID,
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> TaskResponse:
    return await service.create_dispute_letter_review_task(current_user, account_id, letter_id)


@router.post(
    "/{account_id}/dispute-letters/{letter_id}/approve",
    response_model=DisputeLetterResponse,
)
async def approve_account_dispute_letter(
    account_id: uuid.UUID,
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> DisputeLetterResponse:
    return await service.approve_dispute_letter(current_user, account_id, letter_id)


@router.post(
    "/{account_id}/dispute-letters/{letter_id}/send",
    response_model=DisputeLetterResponse,
)
async def send_account_dispute_letter(
    account_id: uuid.UUID,
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> DisputeLetterResponse:
    return await service.send_dispute_letter(current_user, account_id, letter_id)


@router.post(
    "/{account_id}/dispute-letters/{letter_id}/void",
    response_model=DisputeLetterResponse,
)
async def void_account_dispute_letter(
    account_id: uuid.UUID,
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> DisputeLetterResponse:
    return await service.void_dispute_letter(current_user, account_id, letter_id)


@router.post("/{account_id}/dispute-awaiting-response", response_model=AccountResponse)
async def mark_account_awaiting_dispute_response(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.mark_account_awaiting_dispute_response(current_user, account_id)


@router.post("/{account_id}/dispute-response-received", response_model=AccountResponse)
async def record_account_dispute_response_received(
    account_id: uuid.UUID,
    body: AccountDisputeResponseReceivedRequest,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.record_dispute_response_received(current_user, account_id, body)


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
