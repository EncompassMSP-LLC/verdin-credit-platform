"""Portal action-plan checklist from published readiness blockers (LRP-104)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.credit_analysis_run_models import CreditAnalysisRun
from api.modules.accounts.credit_analysis_run_repository import CreditAnalysisRunRepository
from api.modules.cases.models import Case
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.checklist_repository import PortalChecklistRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalChecklistItemResponse,
    PortalChecklistResponse,
)
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository

# Baseline action-plan items always shown once a case is linked (parity with readiness UX).
_BASELINE_ITEMS: list[dict[str, str]] = [
    {
        "key": "baseline:review-readiness",
        "title": "Review your Lending Readiness Score™ band",
        "category": "Readiness",
        "priority": "medium",
        "description": "Open Readiness to understand your advisory band and current blockers.",
    },
    {
        "key": "baseline:upload-documents",
        "title": "Upload any documents your advisor requested",
        "category": "Documents",
        "priority": "medium",
        "description": "Use Documents to add ID or supporting files. Never upload someone else’s documents.",
    },
    {
        "key": "baseline:ask-advisor",
        "title": "Ask your advisor a question if anything is unclear",
        "category": "Messages",
        "priority": "low",
        "description": "Use Messages for staff-mediated questions — task copy never promises bureau outcomes.",
    },
]


class ClientPortalChecklistService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)
        self._completions = PortalChecklistRepository(session)
        self._runs = CreditAnalysisRunRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalChecklistService:
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def _resolve_client_context(
        self,
        portal_user: ClientPortalUser,
    ) -> tuple[Client, list[str]]:
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
        return client, contact_emails

    async def _require_case(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> Case:
        client, contact_emails = await self._resolve_client_context(portal_user)
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
        return case

    async def _latest_published_run(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> CreditAnalysisRun | None:
        return await self._runs.get_latest_for_case(
            organization_id=organization_id,
            case_id=case_id,
            status="published",
        )

    def _catalog_from_run(self, run: CreditAnalysisRun | None) -> list[dict[str, str]]:
        items = list(_BASELINE_ITEMS)
        if run is None:
            return items
        blockers = (run.payload or {}).get("blockers") or []
        for blocker in blockers:
            key = f"blocker:{blocker.get('id', '')}"
            if not blocker.get("id"):
                continue
            items.append(
                {
                    "key": key,
                    "title": str(blocker.get("title") or "Readiness blocker"),
                    "category": "Blocker",
                    "priority": "high",
                    "description": str(blocker.get("action") or blocker.get("impact") or ""),
                }
            )
        return items

    async def list_checklist(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalChecklistResponse:
        self._require_enabled()
        case = await self._require_case(portal_user, case_id)
        run = await self._latest_published_run(
            organization_id=portal_user.organization_id,
            case_id=case.id,
        )
        catalog = self._catalog_from_run(run)
        completions = await self._completions.list_for_case_user(
            organization_id=portal_user.organization_id,
            case_id=case.id,
            portal_user_id=portal_user.id,
        )
        status_by_key = {row.item_key: row for row in completions}
        now = datetime.now(UTC)
        items: list[PortalChecklistItemResponse] = []
        for index, entry in enumerate(catalog):
            row = status_by_key.get(entry["key"])
            items.append(
                PortalChecklistItemResponse(
                    id=entry["key"],
                    case_id=case.id,
                    title=entry["title"],
                    category=entry["category"],
                    priority=entry["priority"],
                    status=row.status if row else "open",
                    due_date=None,
                    sort_order=index,
                    updated_at=row.updated_at
                    if row
                    else ((run.published_at or run.generated_at) if run else now),
                    description=entry.get("description") or None,
                )
            )
        return PortalChecklistResponse(case_id=case.id, items=items)

    async def update_item(
        self,
        portal_user: ClientPortalUser,
        item_id: str,
        *,
        new_status: str,
    ) -> PortalChecklistItemResponse:
        self._require_enabled()
        if new_status not in {"open", "done"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="status must be open or done",
            )
        if ":" not in item_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist item not found",
            )

        # Resolve case by scanning portal user's cases for a matching catalog key.
        client, contact_emails = await self._resolve_client_context(portal_user)
        cases = await self._cases.list_cases_for_client(
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        matched_case = None
        matched_entry: dict[str, str] | None = None
        for case in cases:
            run = await self._latest_published_run(
                organization_id=portal_user.organization_id,
                case_id=case.id,
            )
            catalog = self._catalog_from_run(run)
            for entry in catalog:
                if entry["key"] == item_id:
                    matched_case = case
                    matched_entry = entry
                    break
            if matched_case is not None:
                break

        if matched_case is None or matched_entry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist item not found",
            )

        row = await self._completions.upsert_status(
            organization_id=portal_user.organization_id,
            case_id=matched_case.id,
            portal_user_id=portal_user.id,
            item_key=item_id,
            status=new_status,
        )
        await self._session.commit()
        return PortalChecklistItemResponse(
            id=item_id,
            case_id=matched_case.id,
            title=matched_entry["title"],
            category=matched_entry["category"],
            priority=matched_entry["priority"],
            status=row.status,
            due_date=None,
            sort_order=0,
            updated_at=row.updated_at,
            description=matched_entry.get("description") or None,
        )
