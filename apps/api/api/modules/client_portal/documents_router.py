"""Client portal document upload endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.documents_service import ClientPortalDocumentsService
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.schemas import PortalCaseDocumentsResponse, PortalDocumentResponse
from api.modules.documents.storage import DocumentStorage, get_document_storage

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_document_storage_dep() -> DocumentStorage:
    return get_document_storage()


def get_portal_documents_service(
    db: AsyncSession = Depends(get_db),
    storage: DocumentStorage = Depends(get_document_storage_dep),
) -> ClientPortalDocumentsService:
    return ClientPortalDocumentsService.from_session(db, storage)


@router.get("/{case_id}/documents", response_model=PortalCaseDocumentsResponse)
async def list_portal_case_documents(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalDocumentsService = Depends(get_portal_documents_service),
) -> PortalCaseDocumentsResponse:
    return await service.list_case_documents(portal_user, case_id)


@router.post(
    "/{case_id}/documents",
    response_model=PortalDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_portal_case_document(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalDocumentsService = Depends(get_portal_documents_service),
) -> PortalDocumentResponse:
    return await service.upload_case_document(
        portal_user,
        case_id,
        file=file,
        title=title,
        description=description,
    )
