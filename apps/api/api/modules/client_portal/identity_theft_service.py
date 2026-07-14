"""Client portal identity-theft confirmation service."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository
from api.modules.documents.identity_theft_repository import IdentityTheftRepository
from api.modules.documents.identity_theft_service import (
    aggregate_case_identity_theft_findings,
    build_case_center,
    confirm_account_review,
)
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from api.modules.documents.repository import DocumentRepository
from api.modules.documents.schemas import (
    ConfirmIdentityTheftAccountRequest,
    IdentityTheftAccountReviewResponse,
    IdentityTheftCaseCenterResponse,
)


class ClientPortalIdentityTheftService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)
        self._documents = DocumentRepository(session)
        self._identity_theft = IdentityTheftRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalIdentityTheftService:
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

    async def _ensure_case_access(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> Client:
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
        return client

    @staticmethod
    def _latest_parsed_reports_by_bureau(
        parsed_reports: list[DocumentParsedCreditReport],
    ) -> dict[str, tuple[uuid.UUID, dict[str, Any]]]:
        latest: dict[str, tuple[uuid.UUID, DocumentParsedCreditReport]] = {}
        for row in parsed_reports:
            current = latest.get(row.bureau)
            if current is None or row.parsed_at >= current[1].parsed_at:
                latest[row.bureau] = (row.document_id, row)
        return {
            bureau: (document_id, row.parsed_report)
            for bureau, (document_id, row) in latest.items()
        }

    async def get_identity_theft_center(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> IdentityTheftCaseCenterResponse:
        self._require_enabled()
        await self._ensure_case_access(portal_user, case_id)
        parsed_reports = await self._documents.list_case_parsed_credit_reports(
            organization_id=portal_user.organization_id,
            case_id=case_id,
        )
        reports_by_bureau = self._latest_parsed_reports_by_bureau(parsed_reports)
        findings = None
        if reports_by_bureau:
            findings = aggregate_case_identity_theft_findings(
                case_id=case_id,
                reports_by_bureau=reports_by_bureau,
            )
        return await build_case_center(
            repo=self._identity_theft,
            organization_id=portal_user.organization_id,
            case_id=case_id,
            findings=findings,
        )

    async def confirm_account(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        request: ConfirmIdentityTheftAccountRequest,
    ) -> IdentityTheftAccountReviewResponse:
        self._require_enabled()
        await self._ensure_case_access(portal_user, case_id)
        return await confirm_account_review(
            repo=self._identity_theft,
            actor_id=portal_user.id,
            organization_id=portal_user.organization_id,
            case_id=case_id,
            request=request,
        )
