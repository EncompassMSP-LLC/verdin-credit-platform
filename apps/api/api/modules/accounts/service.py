"""Account management service — business logic and intelligence."""

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.events import publish_platform_event
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.dispute_drafts import (
    build_dispute_body,
    build_dispute_reasons,
    build_evidence_checklist,
)
from api.modules.accounts.intelligence import apply_account_intelligence, recommend_next_action
from api.modules.accounts.models import Account
from api.modules.accounts.permissions import ACCOUNT_DELETE_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountListFilters, AccountRepository
from api.modules.accounts.schemas import (
    AccountCreate,
    AccountDisputeDraftResponse,
    AccountIntelligenceSummary,
    AccountListParams,
    AccountResponse,
    AccountUpdate,
    NextActionItem,
)
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.tasks.models import Task, TaskPriority
from api.modules.tasks.repository import TaskRepository
from api.modules.tasks.schemas import TaskResponse
from api.modules.timeline.builders import (
    account_created_event,
    account_status_changed_event,
    account_updated_event,
    task_created_event,
)
from api.repositories.account import AccountRepositoryProtocol

DISPUTE_DRAFT_REVIEW_TASK_SOURCE = "accounts.dispute_draft"


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        case_repo: CaseRepository | None = None,
        task_repo: TaskRepository | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self._accounts = account_repo
        self._cases = case_repo
        self._tasks = task_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "AccountService":
        return cls(
            AccountRepository(session),
            CaseRepository(session),
            TaskRepository(session),
            session=session,
        )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify accounts",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete accounts",
            )

    async def _validate_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        if self._cases is None:
            return
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case must belong to the same organization",
            )

    async def _get_account_for_user(self, account_id: uuid.UUID, user: User) -> Account:
        organization_id = self._require_organization(user)
        account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return account

    @staticmethod
    def _filters_from_params(
        organization_id: uuid.UUID,
        params: AccountListParams,
    ) -> AccountListFilters:
        return AccountListFilters(
            organization_id=organization_id,
            search=params.search,
            case_id=params.case_id,
            bureau=params.bureau,
            account_type=params.account_type,
            account_status=params.account_status,
            payment_status=params.payment_status,
            dispute_status=params.dispute_status,
            min_risk_score=params.min_risk_score,
            max_risk_score=params.max_risk_score,
            min_readiness_score=params.min_readiness_score,
            dispute_ready=params.dispute_ready,
            skip=params.offset,
            limit=params.page_size,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )

    async def create_account(self, user: User, data: AccountCreate) -> AccountResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._validate_case(data.case_id, organization_id)

        account = Account(
            organization_id=organization_id,
            case_id=data.case_id,
            bureau=data.bureau,
            creditor_name=data.creditor_name,
            original_creditor=data.original_creditor,
            account_number_masked=data.account_number_masked,
            account_type=data.account_type,
            account_status=data.account_status,
            payment_status=data.payment_status,
            balance=data.balance,
            high_balance=data.high_balance,
            credit_limit=data.credit_limit,
            monthly_payment=data.monthly_payment,
            past_due_amount=data.past_due_amount,
            date_opened=data.date_opened,
            date_reported=data.date_reported,
            date_last_activity=data.date_last_activity,
            date_first_delinquency=data.date_first_delinquency,
            estimated_removal_date=data.estimated_removal_date,
            responsibility=data.responsibility,
            remarks=data.remarks,
            dispute_round=data.dispute_round,
            investigation_status=data.investigation_status,
            last_dispute_date=data.last_dispute_date,
            response_received=data.response_received,
            cra_dispute=data.cra_dispute,
            furnisher_dispute=data.furnisher_dispute,
            cfpb_dispute=data.cfpb_dispute,
            ai_summary=data.ai_summary,
            ai_recommended_next_action=data.ai_recommended_next_action,
        )
        if data.dispute_status is not None:
            account.dispute_status = data.dispute_status

        apply_account_intelligence(account)
        apply_audit_on_create(account, user.id)
        created = await self._accounts.create(account)
        if self._session is not None:
            await publish_platform_event(self._session, account_created_event(created, user.id))
        return AccountResponse.from_model(created)

    async def list_accounts(
        self,
        user: User,
        params: AccountListParams,
    ) -> PaginatedResponse[AccountResponse]:
        organization_id = self._require_organization(user)
        filters = self._filters_from_params(organization_id, params)
        items, total = await self._accounts.list_accounts(filters)
        return paginate(
            [AccountResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def list_case_accounts(
        self,
        user: User,
        case_id: uuid.UUID,
        params: AccountListParams,
    ) -> PaginatedResponse[AccountResponse]:
        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        scoped = params.model_copy(update={"case_id": case_id})
        return await self.list_accounts(user, scoped)

    async def get_account(self, user: User, account_id: uuid.UUID) -> AccountResponse:
        account = await self._get_account_for_user(account_id, user)
        return AccountResponse.from_model(account)

    async def get_dispute_draft(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> AccountDisputeDraftResponse:
        account = await self._get_account_for_user(account_id, user)
        if self._cases is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Case repository is not configured",
            )
        case = await self._cases.get_by_id(
            account.case_id,
            organization_id=account.organization_id,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        disputed_items = build_dispute_reasons(account)
        return AccountDisputeDraftResponse(
            account_id=account.id,
            case_id=account.case_id,
            bureau=account.bureau,
            recipient_type="credit_bureau",
            template_id="cra-tradeline-investigation-v1",
            subject=f"Dispute of {account.creditor_name} tradeline",
            body=build_dispute_body(account, case, disputed_items),
            disputed_items=disputed_items,
            requested_action=(
                "Investigate the disputed tradeline and delete or correct any information "
                "that cannot be verified as complete and accurate."
            ),
            evidence_checklist=build_evidence_checklist(account),
            compliance_notes=[
                "Draft requires staff review before sending.",
                "Confirm consumer authorization and supporting evidence before submission.",
            ],
            generated_by="rules",
            readiness_score=account.readiness_score,
            risk_score=account.risk_score,
        )

    async def create_dispute_draft_review_task(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> TaskResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._tasks is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task repository is not configured",
            )

        existing = await self._tasks.find_active_by_account_source(
            organization_id=account.organization_id,
            account_id=account.id,
            source_module=DISPUTE_DRAFT_REVIEW_TASK_SOURCE,
            source_event_id=account.id,
        )
        if existing is not None:
            return TaskResponse.from_model(existing)

        task = Task(
            organization_id=account.organization_id,
            case_id=account.case_id,
            account_id=account.id,
            title=f"Review dispute draft for {account.creditor_name}",
            description=(
                "Review the rule-based CRA dispute draft, confirm supporting evidence, "
                "and prepare the next dispute action."
            ),
            priority=TaskPriority.HIGH,
            due_date=datetime.now(UTC) + timedelta(days=1),
            source_module=DISPUTE_DRAFT_REVIEW_TASK_SOURCE,
            source_event_id=account.id,
        )
        apply_audit_on_create(task, user.id)
        created = await self._tasks.create(task)
        if self._session is not None:
            await publish_platform_event(self._session, task_created_event(created, user.id))
        return TaskResponse.from_model(created)

    async def update_account(
        self,
        user: User,
        account_id: uuid.UUID,
        data: AccountUpdate,
    ) -> AccountResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        previous_account_status = account.account_status
        previous_payment_status = account.payment_status

        update_data = data.model_dump(exclude_unset=True)
        preserved_dispute = update_data.pop("dispute_status", None)
        preserved_action = update_data.pop("ai_recommended_next_action", None)
        for field, value in update_data.items():
            setattr(account, field, value)

        apply_account_intelligence(account)
        if preserved_dispute is not None:
            account.dispute_status = preserved_dispute
        if preserved_action is not None:
            account.ai_recommended_next_action = preserved_action
        apply_audit_on_update(account, user.id)
        updated = await self._accounts.update(account)
        if self._session is not None:
            await publish_platform_event(self._session, account_updated_event(updated, user.id))
            status_changed = (
                "account_status" in update_data
                and updated.account_status != previous_account_status
            ) or (
                "payment_status" in update_data
                and updated.payment_status != previous_payment_status
            )
            if status_changed:
                prev = (
                    previous_account_status.value
                    if hasattr(previous_account_status, "value")
                    else str(previous_account_status)
                )
                await publish_platform_event(
                    self._session,
                    account_status_changed_event(updated, user.id, previous_status=prev),
                )
        return AccountResponse.from_model(updated)

    async def delete_account(self, user: User, account_id: uuid.UUID) -> None:
        self._require_delete(user)
        account = await self._get_account_for_user(account_id, user)
        account.soft_delete()
        apply_audit_on_update(account, user.id)
        await self._accounts.update(account)

    async def get_intelligence_summary(
        self,
        user: User,
        *,
        case_id: uuid.UUID | None = None,
    ) -> AccountIntelligenceSummary:
        organization_id = self._require_organization(user)
        if case_id is not None:
            await self._validate_case(case_id, organization_id)

        raw = await self._accounts.get_intelligence_summary(organization_id, case_id=case_id)
        next_action_queue = [
            NextActionItem(
                account_id=account.id,
                case_id=account.case_id,
                creditor_name=account.creditor_name,
                bureau=account.bureau,
                dispute_status=account.dispute_status,
                risk_score=account.risk_score,
                readiness_score=account.readiness_score,
                recommended_action=account.ai_recommended_next_action
                or recommend_next_action(account),
            )
            for account in raw["next_action_queue"]
        ]

        return AccountIntelligenceSummary(
            total_accounts=raw["total_accounts"],
            total_balance=raw["total_balance"],
            collection_count=raw["collection_count"],
            charge_off_count=raw["charge_off_count"],
            critical_accounts=raw["critical_accounts"],
            dispute_ready_count=raw["dispute_ready_count"],
            evidence_needed_count=raw["evidence_needed_count"],
            total_past_due=raw["total_past_due"],
            accounts_by_bureau=raw["accounts_by_bureau"],
            accounts_by_type=raw["accounts_by_type"],
            accounts_by_status=raw["accounts_by_status"],
            highest_balance_accounts=[
                AccountResponse.from_model(a) for a in raw["highest_balance_accounts"]
            ],
            highest_risk_accounts=[
                AccountResponse.from_model(a) for a in raw["highest_risk_accounts"]
            ],
            next_action_queue=next_action_queue,
        )
