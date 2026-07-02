"""LLM-powered case summary generation."""

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
from api.core.permissions import has_permission
from api.modules.accounts.models import Account
from api.modules.accounts.repository import AccountListFilters, AccountRepository
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.permissions import CASE_WRITE_ROLE
from api.modules.cases.repository import CaseRepository
from api.modules.cases.schemas import CaseLlmSummaryResponse
from api.modules.timeline.builders import case_llm_summary_event


class CaseLlmSummaryService:
    def __init__(
        self,
        case_repo: CaseRepository,
        account_repo: AccountRepository,
        session: AsyncSession | None = None,
        llm_client: LlmCompletionClient | None = None,
    ) -> None:
        self._cases = case_repo
        self._accounts = account_repo
        self._session = session
        self._llm_client = llm_client

    @classmethod
    def from_session(cls, session: AsyncSession) -> CaseLlmSummaryService:
        return cls(CaseRepository(session), AccountRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to generate case summaries",
            )

    async def _get_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case

    @staticmethod
    def _build_case_context(case: Case, accounts: list[Account]) -> dict[str, object]:
        account_rows: list[dict[str, object]] = []
        for account in accounts:
            account_rows.append(
                {
                    "bureau": account.bureau.value,
                    "account_type": account.account_type.value,
                    "account_status": account.account_status.value,
                    "dispute_status": account.dispute_status.value,
                    "risk_score": account.risk_score,
                    "readiness_score": account.readiness_score,
                    "creditor_name": account.creditor_name,
                }
            )

        return {
            "case": {
                "title": case.title,
                "status": case.status.value,
                "stage": case.stage.value,
                "priority": case.priority.value,
                "case_number": case.case_number,
                "client_name": case.client_name,
                "client_email": case.client_email,
                "summary": case.summary,
                "notes": case.notes,
            },
            "accounts": account_rows,
        }

    @staticmethod
    def _build_prompt(context: dict[str, object]) -> tuple[str, str]:
        system_prompt = (
            "You are a credit repair operations assistant. Summarize the case context "
            "for staff review. Focus on status, dispute readiness, risks, and recommended "
            "next actions. Do not invent facts not present in the context."
        )
        user_prompt = (
            "Generate a concise case summary from this scrubbed JSON context:\n"
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

    async def generate_summary(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseLlmSummaryResponse:
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

        case = await self._get_case(case_id, organization_id)
        accounts, _ = await self._accounts.list_accounts(
            AccountListFilters(
                organization_id=organization_id,
                case_id=case_id,
                skip=0,
                limit=50,
            )
        )

        raw_context = self._build_case_context(case, accounts)
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
                detail=str(exc),
            ) from exc

        generated_at = datetime.now(UTC)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                case_llm_summary_event(
                    case=case,
                    performed_by=user.id,
                    model=completion.model,
                    provider=completion.provider,
                    prompt_hash=prompt_hash,
                    generated_at=generated_at,
                ),
            )

        return CaseLlmSummaryResponse(
            case_id=case.id,
            summary=completion.content,
            model=completion.model,
            provider=completion.provider,
            prompt_hash=prompt_hash,
            generated_at=generated_at,
            pii_scrubbed=True,
        )
