"""Client portal document upload service — scoped to linked cases."""

import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import PortalCaseDocumentsResponse, PortalDocumentResponse
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository
from api.modules.documents.models import Document
from api.modules.documents.service import DocumentService
from api.modules.documents.storage import DocumentStorage, get_document_storage


class ClientPortalDocumentsService:
    def __init__(
        self,
        session: AsyncSession,
        document_service: DocumentService,
    ) -> None:
        self._session = session
        self._documents = document_service
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        storage: DocumentStorage | None = None,
    ) -> "ClientPortalDocumentsService":
        document_storage = storage or get_document_storage()
        return cls(session, DocumentService.from_session(session, document_storage))

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
    ) -> None:
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

    @staticmethod
    def _to_portal_document(document: Document) -> PortalDocumentResponse:
        return PortalDocumentResponse(
            id=document.id,
            case_id=document.case_id,
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            mime_type=document.mime_type,
            file_size=document.file_size,
            processing_status=document.processing_status,
            created_at=document.created_at,
        )

    async def list_case_documents(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalCaseDocumentsResponse:
        self._require_enabled()
        await self._ensure_case_access(portal_user, case_id)
        documents = await self._documents.list_documents_for_case(
            organization_id=portal_user.organization_id,
            case_id=case_id,
        )
        return PortalCaseDocumentsResponse(
            items=[self._to_portal_document(document) for document in documents]
        )

    async def upload_case_document(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        *,
        file: UploadFile,
        title: str,
        description: str | None = None,
    ) -> PortalDocumentResponse:
        self._require_enabled()
        await self._ensure_case_access(portal_user, case_id)
        document = await self._documents.upload_document_for_portal(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
            case_id=case_id,
            file=file,
            title=title,
            description=description,
        )
        return self._to_portal_document(document)
