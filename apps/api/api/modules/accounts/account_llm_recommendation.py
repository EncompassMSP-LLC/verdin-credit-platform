"""LLM-powered account recommendation generation."""

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
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.llm import require_llm_gateway
from api.core.permissions import has_permission
from api.modules.accounts.intelligence_context import (
    build_discrepancy_context_map,
    compare_case_reports,
    discrepancy_context_for_account,
)
from api.modules.accounts.models import Account
from api.modules.accounts.permissions import ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountRepository
from api.modules.accounts.schemas import AccountLlmRecommendationResponse
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.documents.repository import DocumentRepository
from api.modules.timeline.builders import account_llm_recommendation_event


class AccountLlmRecommendationService:
    def __init__(
        self,
        account_repo: AccountRepository,
        case_repo: CaseRepository,
        document_repo: DocumentRepository,
        session: AsyncSession | None = None,
        llm_client: LlmCompletionClient | None = None,
    ) -> None:
        self._accounts = account_repo
        self._cases = case_repo
        self._documents = document_repo
        self._session = session
        self._llm_client = llm_client

    @classmethod
    def from_session(cls, session: AsyncSession) -> AccountLlmRecommendationService:
        return cls(
            AccountRepository(session),
            CaseRepository(session),
            DocumentRepository(session),
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
                detail="Insufficient permissions to generate account recommendations",
            )

    def _require_feature(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_LLM_ACCOUNT_RECOMMENDATIONS):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM account recommendations are not enabled",
            )

    async def _get_account(self, account_id: uuid.UUID, organization_id: uuid.UUID) -> Account:
        account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return account

    async def _get_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case

    async def _cross_bureau_context(self, account: Account) -> dict[str, object] | None:
        parsed_reports = await self._documents.list_case_parsed_credit_reports(
            organization_id=account.organization_id,
            case_id=account.case_id,
        )
        reports_by_bureau: dict[str, tuple[uuid.UUID, dict[str, object]]] = {}
        for parsed_report in parsed_reports:
            bureau = str(parsed_report.bureau).lower()
            if bureau in reports_by_bureau:
                continue
            reports_by_bureau[bureau] = (parsed_report.document_id, parsed_report.parsed_report)
        if len(reports_by_bureau) < 2:
            return None

        result = compare_case_reports(
            case_id=account.case_id,
            reports_by_bureau=reports_by_bureau,
        )
        context_map = build_discrepancy_context_map(result.discrepancies)
        discrepancy = discrepancy_context_for_account(account, context_map)
        if discrepancy is None:
            return None
        return {
            "match_key": discrepancy.match_key,
            "classification": discrepancy.classification,
            "confidence_score": discrepancy.confidence_score,
            "dispute_ready": discrepancy.dispute_ready,
            "requires_investigation": discrepancy.requires_investigation,
            "discrepancy_types": list(discrepancy.discrepancy_types),
            "recommended_action": discrepancy.recommended_action,
        }

    @staticmethod
    def _build_account_context(
        account: Account,
        case: Case,
        cross_bureau: dict[str, object] | None,
    ) -> dict[str, object]:
        return {
            "case": {
                "title": case.title,
                "status": case.status.value,
                "stage": case.stage.value,
                "priority": case.priority.value,
            },
            "account": {
                "creditor_name": account.creditor_name,
                "bureau": account.bureau.value,
                "account_type": account.account_type.value,
                "account_status": account.account_status.value,
                "payment_status": account.payment_status.value,
                "dispute_status": account.dispute_status.value,
                "investigation_status": account.investigation_status.value,
                "risk_score": account.risk_score,
                "readiness_score": account.readiness_score,
                "balance": str(account.balance) if account.balance is not None else None,
                "past_due_amount": (
                    str(account.past_due_amount) if account.past_due_amount is not None else None
                ),
                "remarks": account.remarks,
                "current_recommendation": account.ai_recommended_next_action,
            },
            "cross_bureau_discrepancy": cross_bureau,
        }

    @staticmethod
    def _build_prompt(context: dict[str, object]) -> tuple[str, str]:
        system_prompt = (
            "You are a credit repair operations assistant. Recommend the single best next "
            "action for staff working this tradeline. Be specific, concise, and grounded "
            "only in the provided context. Return plain text with no markdown."
        )
        user_prompt = (
            "Generate one recommended next action from this scrubbed JSON context:\n"
            f"{json.dumps(context, indent=2, default=str)}"
        )
        return system_prompt, user_prompt

    @staticmethod
    def _prompt_hash(system_prompt: str, user_prompt: str) -> str:
        digest = hashlib.sha256()
        digest.update(system_prompt.encode("utf-8"))
        digest.update(b"\n")
        digest.update(user_prompt.encode("utf-8"))
        return digest.hexdigest()

    async def generate_recommendation(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> AccountLlmRecommendationResponse:
        self._require_feature()
        self._require_write(user)
        organization_id = self._require_organization(user)

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
        case = await self._get_case(account.case_id, organization_id)
        cross_bureau = await self._cross_bureau_context(account)
        raw_context = self._build_account_context(account, case, cross_bureau)
        scrubbed_context = scrub_payload(raw_context)
        system_prompt, user_prompt = self._build_prompt(scrubbed_context)
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
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM provider request failed: {exc}",
            ) from exc

        recommendation = completion.content.strip()
        account.ai_recommended_next_action = recommendation
        updated = await self._accounts.update(account)

        generated_at = datetime.now(UTC)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                account_llm_recommendation_event(
                    updated,
                    user.id,
                    provider=gate_status.provider,
                    model=gate_status.model,
                    prompt_hash=prompt_hash,
                ),
            )

        return AccountLlmRecommendationResponse(
            account_id=updated.id,
            recommendation=recommendation,
            provider=gate_status.provider,
            model=gate_status.model,
            prompt_hash=prompt_hash,
            pii_scrubbed=True,
            generated_at=generated_at,
            cross_bureau_informed=cross_bureau is not None,
        )
