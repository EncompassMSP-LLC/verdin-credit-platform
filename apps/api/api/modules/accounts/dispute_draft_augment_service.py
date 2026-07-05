"""LLM dispute draft augment service."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_llm_gateway import (
    LlmChatMessage,
    LlmCompletionClient,
    LlmFeatureDisabledError,
    LlmPiiPolicyError,
    LlmProviderNotConfiguredError,
    get_llm_completion_client,
    get_llm_settings,
    scrub_payload,
)

from api.core.events import publish_platform_event
from api.core.llm import require_llm_gateway
from api.core.llm_dispute_draft_augment import get_llm_dispute_draft_augment_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.dispute_draft_augment_models import LlmDisputeDraftAugmentStatus
from api.modules.accounts.dispute_draft_augment_repository import (
    LlmDisputeDraftAugmentListFilters,
    LlmDisputeDraftAugmentRepository,
)
from api.modules.accounts.dispute_draft_augment_schemas import (
    LlmDisputeDraftAugmentListParams,
    LlmDisputeDraftAugmentRequest,
    LlmDisputeDraftAugmentResponse,
    LlmDisputeDraftAugmentStatusResponse,
)
from api.modules.accounts.dispute_drafts import (
    CRA_TEMPLATE_ID,
    FURNISHER_TEMPLATE_ID,
    DisputeRecipientType,
    build_dispute_body,
    build_dispute_reasons,
    build_furnisher_dispute_body,
)
from api.modules.accounts.models import Account
from api.modules.accounts.permissions import ACCOUNT_READ_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.timeline.builders import dispute_draft_llm_augment_event


class LlmDisputeDraftAugmentService:
    def __init__(
        self,
        account_repo: AccountRepository,
        case_repo: CaseRepository,
        augment_repo: LlmDisputeDraftAugmentRepository,
        session: AsyncSession | None = None,
        llm_client: LlmCompletionClient | None = None,
    ) -> None:
        self._accounts = account_repo
        self._cases = case_repo
        self._augments = augment_repo
        self._session = session
        self._llm_client = llm_client

    @classmethod
    def from_session(cls, session: AsyncSession) -> LlmDisputeDraftAugmentService:
        return cls(
            AccountRepository(session),
            CaseRepository(session),
            LlmDisputeDraftAugmentRepository(session),
            session=session,
        )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view dispute draft augments",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to augment dispute drafts",
            )

    def get_status_response(self) -> LlmDisputeDraftAugmentStatusResponse:
        return LlmDisputeDraftAugmentStatusResponse.from_status(
            get_llm_dispute_draft_augment_status()
        )

    async def _get_account(self, account_id: uuid.UUID, organization_id: uuid.UUID) -> Account:
        account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return account

    @staticmethod
    def _build_base_draft(
        *,
        account: Account,
        case: Case,
        recipient_type: DisputeRecipientType,
    ) -> tuple[str, str, str]:
        disputed_items = build_dispute_reasons(account)
        if recipient_type == "furnisher":
            template_id = FURNISHER_TEMPLATE_ID
            subject = f"Direct furnisher dispute — {account.creditor_name} tradeline"
            body = build_furnisher_dispute_body(account, case, disputed_items)
        else:
            template_id = CRA_TEMPLATE_ID
            subject = f"Dispute of {account.creditor_name} tradeline"
            body = build_dispute_body(account, case, disputed_items)
        return template_id, subject, body

    @staticmethod
    def _build_prompt(
        *,
        base_subject: str,
        base_body: str,
        context: dict[str, object],
    ) -> tuple[str, str]:
        system_prompt = (
            "You are a credit repair operations assistant. Improve the dispute letter "
            "draft for staff review. Preserve factual claims from the rule-based draft "
            "and scrubbed context. Do not invent tradeline facts. Return only the revised "
            "letter body text without markdown fences."
        )
        user_prompt = (
            "Improve this dispute letter draft using the scrubbed JSON context.\n\n"
            f"Subject: {base_subject}\n\n"
            f"Current body:\n{base_body}\n\n"
            f"Context JSON:\n{json.dumps(context, indent=2, default=str)}"
        )
        return system_prompt, user_prompt

    @staticmethod
    def _prompt_hash(system_prompt: str, user_prompt: str) -> str:
        digest = hashlib.sha256()
        digest.update(system_prompt.encode("utf-8"))
        digest.update(b"\n")
        digest.update(user_prompt.encode("utf-8"))
        return digest.hexdigest()

    async def list_augments(
        self,
        user: User,
        account_id: uuid.UUID,
        params: LlmDisputeDraftAugmentListParams,
    ) -> PaginatedResponse[LlmDisputeDraftAugmentResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        await self._get_account(account_id, organization_id)
        skip = (params.page - 1) * params.page_size
        augments, total = await self._augments.list_augments_for_account(
            organization_id,
            account_id,
            LlmDisputeDraftAugmentListFilters(skip=skip, limit=params.page_size),
        )
        items = [LlmDisputeDraftAugmentResponse.from_model(item) for item in augments]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def augment_draft(
        self,
        user: User,
        account_id: uuid.UUID,
        body: LlmDisputeDraftAugmentRequest,
    ) -> LlmDisputeDraftAugmentResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        augment_status = get_llm_dispute_draft_augment_status()
        if not augment_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "LLM dispute draft augment is not ready",
                    "blockers": list(augment_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            gate_status = require_llm_gateway()
        except LlmFeatureDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except LlmProviderNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except LlmPiiPolicyError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        account = await self._get_account(account_id, organization_id)
        case = await self._cases.get_by_id(account.case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        recipient_type: DisputeRecipientType = body.recipient_type
        template_id, subject, base_body = self._build_base_draft(
            account=account,
            case=case,
            recipient_type=recipient_type,
        )
        requested_at = datetime.now(UTC)

        context = scrub_payload(
            {
                "account": {
                    "bureau": account.bureau.value,
                    "creditor_name": account.creditor_name,
                    "dispute_status": account.dispute_status.value,
                    "readiness_score": account.readiness_score,
                    "risk_score": account.risk_score,
                },
                "case": {
                    "title": case.title,
                    "status": case.status.value,
                    "client_name": case.client_name,
                },
                "recipient_type": recipient_type,
            }
        )
        system_prompt, user_prompt = self._build_prompt(
            base_subject=subject,
            base_body=base_body,
            context=context,
        )
        prompt_hash = self._prompt_hash(system_prompt, user_prompt)

        client = self._llm_client or get_llm_completion_client(get_llm_settings())
        try:
            completion = await client.complete(
                [
                    LlmChatMessage(role="system", content=system_prompt),
                    LlmChatMessage(role="user", content=user_prompt),
                ],
                model=gate_status.model,
            )
        except RuntimeError as exc:
            await self._augments.create_augment(
                organization_id=organization_id,
                account_id=account.id,
                case_id=case.id,
                recipient_type=recipient_type,
                base_template_id=template_id,
                base_subject=subject,
                base_body=base_body,
                status=LlmDisputeDraftAugmentStatus.FAILED,
                requested_by_user_id=user.id,
                requested_at=requested_at,
                completed_at=datetime.now(UTC),
                error_message=str(exc),
            )
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        completed_at = datetime.now(UTC)
        augment = await self._augments.create_augment(
            organization_id=organization_id,
            account_id=account.id,
            case_id=case.id,
            recipient_type=recipient_type,
            base_template_id=template_id,
            base_subject=subject,
            base_body=base_body,
            augmented_body=completion.content,
            status=LlmDisputeDraftAugmentStatus.COMPLETED,
            provider=completion.provider,
            model=completion.model,
            prompt_hash=prompt_hash,
            requested_by_user_id=user.id,
            requested_at=requested_at,
            completed_at=completed_at,
        )
        await publish_platform_event(
            self._session,
            dispute_draft_llm_augment_event(
                augment=augment,
                performed_by=user.id,
            ),
        )
        await self._session.commit()
        return LlmDisputeDraftAugmentResponse.from_model(augment)
