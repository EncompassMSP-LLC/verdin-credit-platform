"""Client portal consent signing service."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository
from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey
from api.modules.compliance.schemas import ConsentRecordResponse, PortalCaseConsentsResponse
from api.modules.compliance.service import ComplianceService
from api.modules.documents.storage import DocumentStorage, get_document_storage


class ClientPortalConsentsService:
    def __init__(
        self,
        session: AsyncSession,
        compliance_service: ComplianceService,
    ) -> None:
        self._session = session
        self._compliance = compliance_service
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        storage: DocumentStorage | None = None,
    ) -> ClientPortalConsentsService:
        document_storage = storage or get_document_storage()
        return cls(session, ComplianceService.from_session(session, document_storage))

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

    async def list_case_consents(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalCaseConsentsResponse:
        self._require_enabled()
        client = await self._ensure_case_access(portal_user, case_id)
        return await self._compliance.list_portal_case_consents(
            organization_id=portal_user.organization_id,
            client_id=client.id,
            case_id=case_id,
        )

    async def preview_case_consent(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        *,
        template_key: ConsentDocumentTemplateKey,
    ) -> tuple[bytes, str]:
        self._require_enabled()
        client = await self._ensure_case_access(portal_user, case_id)
        return await self._compliance.preview_portal_consent_document(
            organization_id=portal_user.organization_id,
            client_id=client.id,
            template_key=template_key,
        )

    async def sign_case_consent(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        *,
        template_key: ConsentDocumentTemplateKey,
        signer_name: str,
        attestation_accepted: bool,
        signature_file: UploadFile | None = None,
        request: Request | None = None,
    ) -> ConsentRecordResponse:
        self._require_enabled()
        client = await self._ensure_case_access(portal_user, case_id)
        metadata: dict[str, Any] = {}
        if request is not None:
            metadata["ip_address"] = request.client.host if request.client else None
            metadata["user_agent"] = request.headers.get("user-agent")

        return await self._compliance.sign_portal_consent(
            organization_id=portal_user.organization_id,
            client_id=client.id,
            case_id=case_id,
            portal_user_id=portal_user.id,
            template_key=template_key,
            signer_name=signer_name,
            attestation_accepted=attestation_accepted,
            signature_file=signature_file,
            signature_metadata=metadata,
        )
