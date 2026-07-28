"""Borrower-safe dispute strategy suggestions for the portal (LRP-403).

Projects the latest staff dispute-strategy run into advisory suggestions.
Never prepares letters, never auto-sends, never contacts bureaus.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalDisputeStrategyAccountSuggestion,
    PortalDisputeStrategyStageSuggestion,
    PortalDisputeStrategySuggestionsResponse,
    PortalDisputeStrategySuggestionsSummary,
)
from api.modules.clients.repository import ClientRepository
from api.modules.documents.strategy_run_repository import StrategyRunRepository

_PORTAL_DISCLAIMER = (
    "Advisory planning suggestions from your readiness team. Not legal advice. "
    "Dispute letters are prepared and sent only by staff after review — "
    "this view never files disputes or contacts bureaus automatically."
)


def _project_stage(stage: dict[str, Any]) -> PortalDisputeStrategyStageSuggestion:
    return PortalDisputeStrategyStageSuggestion(
        stage_kind=str(stage.get("stage_kind") or ""),
        title=str(stage.get("title") or "Next step"),
        objective=str(stage.get("objective") or ""),
        recommended=bool(stage.get("recommended")),
    )


def _project_account(item: dict[str, Any]) -> PortalDisputeStrategyAccountSuggestion:
    stages = [_project_stage(stage) for stage in (item.get("stages") or [])]
    recommended = [stage.title for stage in stages if stage.recommended]
    creditor = str(item.get("creditor_name") or "").strip() or "Account"
    masked = item.get("account_number_masked")
    return PortalDisputeStrategyAccountSuggestion(
        creditor_label=creditor,
        account_number_masked=str(masked) if masked else None,
        summary=str(item.get("summary") or "Staff is reviewing next dispute steps."),
        recommended_stage_titles=recommended,
        stages=stages,
    )


def project_strategy_payload(
    *,
    case_id: uuid.UUID,
    payload: dict[str, Any],
    generated_at: datetime | None,
) -> PortalDisputeStrategySuggestionsResponse:
    summary_raw = payload.get("summary") or {}
    suggestions = [
        _project_account(item)
        for item in (payload.get("strategies") or [])
        if isinstance(item, dict)
    ]
    return PortalDisputeStrategySuggestionsResponse(
        case_id=case_id,
        disclaimer=_PORTAL_DISCLAIMER,
        staff_mediated=True,
        auto_send=False,
        source="staff_run",
        generated_at=generated_at,
        summary=PortalDisputeStrategySuggestionsSummary(
            accounts_planned=int(summary_raw.get("accounts_planned") or 0),
            issues_covered=int(summary_raw.get("issues_covered") or 0),
            high_strength_accounts=int(summary_raw.get("high_strength_accounts") or 0),
            cfpb_recommended=int(summary_raw.get("cfpb_recommended") or 0),
            attorney_recommended=int(summary_raw.get("attorney_recommended") or 0),
        ),
        suggestions=suggestions,
    )


class ClientPortalDisputeStrategyService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)
        self._runs = StrategyRunRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalDisputeStrategyService:
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def get_suggestions(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalDisputeStrategySuggestionsResponse:
        self._require_enabled()
        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )
        contact_emails = await self._cases.list_contact_emails(
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
        )
        case = await self._cases.get_case_for_client(
            case_id,
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        run = await self._runs.get_latest_for_case(
            organization_id=portal_user.organization_id,
            case_id=case.id,
        )
        if run is None:
            return PortalDisputeStrategySuggestionsResponse(
                case_id=case.id,
                disclaimer=_PORTAL_DISCLAIMER,
                staff_mediated=True,
                auto_send=False,
                source="none",
                generated_at=None,
                summary=PortalDisputeStrategySuggestionsSummary(),
                suggestions=[],
            )

        payload = run.payload if isinstance(run.payload, dict) else {}
        return project_strategy_payload(
            case_id=case.id,
            payload=payload,
            generated_at=run.generated_at,
        )
