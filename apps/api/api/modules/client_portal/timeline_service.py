"""Portal readiness timeline — borrower-safe composed events (LRP-401)."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.credit_analysis_run_repository import (
    CreditAnalysisRunListFilters,
    CreditAnalysisRunRepository,
)
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.checklist_repository import PortalChecklistRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import (
    PortalTimelineItemResponse,
    PortalTimelineResponse,
)
from api.modules.clients.repository import ClientRepository
from api.modules.documents.service import DocumentService
from api.modules.documents.storage import get_document_storage

_BAND_LABELS = {
    "building": "Building",
    "progressing": "Progressing",
    "near_ready": "Near Ready",
    "lending_ready": "Lending Ready",
}


class ClientPortalTimelineService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)
        self._runs = CreditAnalysisRunRepository(session)
        self._completions = PortalChecklistRepository(session)
        self._documents = DocumentService.from_session(session, get_document_storage())

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalTimelineService:
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def list_timeline(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        *,
        event_type: str | None = None,
    ) -> PortalTimelineResponse:
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

        items: list[PortalTimelineItemResponse] = [
            PortalTimelineItemResponse(
                id=f"case-opened-{case.id}",
                event_at=case.opened_at,
                event_type="case",
                title="Case opened",
                detail=f"{case.title} · stage {case.stage.value.replace('_', ' ')}",
                href="/portal/progress",
            )
        ]

        runs, _ = await self._runs.list_for_case(
            CreditAnalysisRunListFilters(
                organization_id=portal_user.organization_id,
                case_id=case.id,
                skip=0,
                limit=20,
            )
        )
        for run in runs:
            if run.status != "published":
                continue
            band = _BAND_LABELS.get(run.band, run.band.replace("_", " ").title())
            items.append(
                PortalTimelineItemResponse(
                    id=f"readiness-{run.id}",
                    event_at=run.published_at or run.generated_at,
                    event_type="readiness",
                    title="Readiness report published",
                    detail=f"Advisory band: {band}",
                    href="/portal/reports",
                )
            )

        documents = await self._documents.list_documents_for_case(
            organization_id=portal_user.organization_id,
            case_id=case.id,
        )
        for document in documents:
            items.append(
                PortalTimelineItemResponse(
                    id=f"document-{document.id}",
                    event_at=document.created_at,
                    event_type="document",
                    title="Document uploaded",
                    detail=document.title,
                    href="/portal/documents",
                )
            )

        completions = await self._completions.list_for_case_user(
            organization_id=portal_user.organization_id,
            case_id=case.id,
            portal_user_id=portal_user.id,
        )
        for row in completions:
            if row.status != "done":
                continue
            items.append(
                PortalTimelineItemResponse(
                    id=f"task-{row.id}",
                    event_at=row.updated_at,
                    event_type="task",
                    title="Action-plan task completed",
                    detail=row.item_key.replace(":", " · ").replace("-", " "),
                    href="/portal/tasks",
                )
            )

        items.sort(key=lambda item: item.event_at, reverse=True)
        if event_type:
            items = [item for item in items if item.event_type == event_type]

        return PortalTimelineResponse(case_id=case.id, items=items)
