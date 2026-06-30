"""Accounts domain schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    DisputeStatus,
    InvestigationStatus,
    PaymentStatus,
)

AccountSortField = Literal[
    "balance",
    "date_reported",
    "risk_score",
    "readiness_score",
    "created_at",
]
AccountSortOrder = Literal["asc", "desc"]


class AccountCreate(BaseSchema):
    case_id: uuid.UUID
    bureau: AccountBureau = AccountBureau.UNKNOWN
    creditor_name: str = Field(min_length=1, max_length=255)
    original_creditor: str | None = Field(default=None, max_length=255)
    account_number_masked: str | None = Field(default=None, max_length=50)
    account_type: AccountType = AccountType.OTHER
    account_status: AccountStatus = AccountStatus.UNKNOWN
    payment_status: PaymentStatus = PaymentStatus.UNKNOWN
    balance: Decimal | None = None
    high_balance: Decimal | None = None
    credit_limit: Decimal | None = None
    monthly_payment: Decimal | None = None
    past_due_amount: Decimal | None = None
    date_opened: date | None = None
    date_reported: date | None = None
    date_last_activity: date | None = None
    date_first_delinquency: date | None = None
    estimated_removal_date: date | None = None
    responsibility: str | None = Field(default=None, max_length=50)
    remarks: str | None = None
    dispute_status: DisputeStatus | None = None
    dispute_round: int = Field(default=0, ge=0)
    investigation_status: InvestigationStatus = InvestigationStatus.NONE
    last_dispute_date: date | None = None
    response_received: bool = False
    cra_dispute: bool = False
    furnisher_dispute: bool = False
    cfpb_dispute: bool = False
    ai_summary: str | None = None
    ai_recommended_next_action: str | None = None


class AccountUpdate(BaseSchema):
    bureau: AccountBureau | None = None
    creditor_name: str | None = Field(default=None, min_length=1, max_length=255)
    original_creditor: str | None = Field(default=None, max_length=255)
    account_number_masked: str | None = Field(default=None, max_length=50)
    account_type: AccountType | None = None
    account_status: AccountStatus | None = None
    payment_status: PaymentStatus | None = None
    balance: Decimal | None = None
    high_balance: Decimal | None = None
    credit_limit: Decimal | None = None
    monthly_payment: Decimal | None = None
    past_due_amount: Decimal | None = None
    date_opened: date | None = None
    date_reported: date | None = None
    date_last_activity: date | None = None
    date_first_delinquency: date | None = None
    estimated_removal_date: date | None = None
    responsibility: str | None = Field(default=None, max_length=50)
    remarks: str | None = None
    dispute_status: DisputeStatus | None = None
    dispute_round: int | None = Field(default=None, ge=0)
    investigation_status: InvestigationStatus | None = None
    last_dispute_date: date | None = None
    response_received: bool | None = None
    cra_dispute: bool | None = None
    furnisher_dispute: bool | None = None
    cfpb_dispute: bool | None = None
    ai_summary: str | None = None
    ai_recommended_next_action: str | None = None


class AccountListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    case_id: uuid.UUID | None = None
    bureau: AccountBureau | None = None
    account_type: AccountType | None = None
    account_status: AccountStatus | None = None
    payment_status: PaymentStatus | None = None
    dispute_status: DisputeStatus | None = None
    min_risk_score: int | None = Field(default=None, ge=0, le=100)
    max_risk_score: int | None = Field(default=None, ge=0, le=100)
    min_readiness_score: int | None = Field(default=None, ge=0, le=100)
    dispute_ready: bool | None = None
    sort_by: AccountSortField = "created_at"
    sort_order: AccountSortOrder = "desc"


class AccountResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID
    bureau: AccountBureau
    creditor_name: str
    original_creditor: str | None
    account_number_masked: str | None
    account_type: AccountType
    account_status: AccountStatus
    payment_status: PaymentStatus
    balance: Decimal | None
    high_balance: Decimal | None
    credit_limit: Decimal | None
    monthly_payment: Decimal | None
    past_due_amount: Decimal | None
    date_opened: date | None
    date_reported: date | None
    date_last_activity: date | None
    date_first_delinquency: date | None
    estimated_removal_date: date | None
    responsibility: str | None
    remarks: str | None
    dispute_status: DisputeStatus
    dispute_round: int
    investigation_status: InvestigationStatus
    last_dispute_date: date | None
    next_eligible_dispute_date: date | None
    response_received: bool
    cra_dispute: bool
    furnisher_dispute: bool
    cfpb_dispute: bool
    ai_summary: str | None
    ai_recommended_next_action: str | None
    risk_score: int | None
    readiness_score: int | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, account: Account) -> "AccountResponse":
        return cls(
            id=account.id,
            organization_id=account.organization_id,
            case_id=account.case_id,
            bureau=account.bureau,
            creditor_name=account.creditor_name,
            original_creditor=account.original_creditor,
            account_number_masked=account.account_number_masked,
            account_type=account.account_type,
            account_status=account.account_status,
            payment_status=account.payment_status,
            balance=account.balance,
            high_balance=account.high_balance,
            credit_limit=account.credit_limit,
            monthly_payment=account.monthly_payment,
            past_due_amount=account.past_due_amount,
            date_opened=account.date_opened,
            date_reported=account.date_reported,
            date_last_activity=account.date_last_activity,
            date_first_delinquency=account.date_first_delinquency,
            estimated_removal_date=account.estimated_removal_date,
            responsibility=account.responsibility,
            remarks=account.remarks,
            dispute_status=account.dispute_status,
            dispute_round=account.dispute_round,
            investigation_status=account.investigation_status,
            last_dispute_date=account.last_dispute_date,
            next_eligible_dispute_date=account.next_eligible_dispute_date,
            response_received=account.response_received,
            cra_dispute=account.cra_dispute,
            furnisher_dispute=account.furnisher_dispute,
            cfpb_dispute=account.cfpb_dispute,
            ai_summary=account.ai_summary,
            ai_recommended_next_action=account.ai_recommended_next_action,
            risk_score=account.risk_score,
            readiness_score=account.readiness_score,
            created_at=account.created_at,
            updated_at=account.updated_at,
            deleted_at=account.deleted_at,
            created_by_id=account.created_by_id,
            updated_by_id=account.updated_by_id,
        )


class NextActionItem(BaseSchema):
    account_id: uuid.UUID
    case_id: uuid.UUID
    creditor_name: str
    bureau: AccountBureau
    dispute_status: DisputeStatus
    risk_score: int | None
    readiness_score: int | None
    recommended_action: str


class AccountIntelligenceSummary(BaseSchema):
    total_accounts: int
    total_balance: Decimal
    collection_count: int
    charge_off_count: int
    critical_accounts: int
    dispute_ready_count: int
    evidence_needed_count: int
    total_past_due: Decimal
    accounts_by_bureau: dict[str, int]
    accounts_by_type: dict[str, int]
    accounts_by_status: dict[str, int]
    highest_balance_accounts: list[AccountResponse]
    highest_risk_accounts: list[AccountResponse]
    next_action_queue: list[NextActionItem]


class AccountDisputeDraftResponse(BaseSchema):
    account_id: uuid.UUID
    case_id: uuid.UUID
    bureau: AccountBureau
    recipient_type: Literal["credit_bureau"]
    template_id: str
    subject: str
    body: str
    disputed_items: list[str]
    requested_action: str
    evidence_checklist: list[str]
    compliance_notes: list[str]
    generated_by: Literal["rules"]
    readiness_score: int | None
    risk_score: int | None
