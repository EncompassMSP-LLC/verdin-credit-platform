"""Document management endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.documents.schemas import (
    DocumentListParams,
    DocumentResponse,
    DocumentSortField,
    DocumentSortOrder,
    DocumentUpdate,
    DocumentVersionResponse,
)
from api.modules.documents.service import DocumentService
from api.modules.documents.storage import DocumentStorage, get_document_storage

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_storage() -> DocumentStorage:
    return get_document_storage()


def get_document_service(
    db: AsyncSession = Depends(get_db),
    storage: DocumentStorage = Depends(get_storage),
) -> DocumentService:
    return DocumentService.from_session(db, storage)


def get_document_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    case_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    is_duplicate: bool | None = None,
    sort_by: DocumentSortField = "created_at",
    sort_order: DocumentSortOrder = "desc",
) -> DocumentListParams:
    return DocumentListParams(
        page=page,
        page_size=page_size,
        search=search,
        case_id=case_id,
        account_id=account_id,
        is_duplicate=is_duplicate,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    case_id: uuid.UUID = Form(...),
    description: str | None = Form(None),
    account_id: uuid.UUID | None = Form(None),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.upload_document(
        current_user,
        file=file,
        title=title,
        case_id=case_id,
        description=description,
        account_id=account_id,
    )


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    params: DocumentListParams = Depends(get_document_list_params),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> PaginatedResponse[DocumentResponse]:
    return await service.list_documents(current_user, params)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.get_document(current_user, document_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    body: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.update_document(current_user, document_id, body)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> None:
    await service.delete_document(current_user, document_id)


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    version: int | None = Query(None, ge=1),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    data, file_name, mime_type = await service.download_document(
        current_user,
        document_id,
        version_number=version,
    )
    return Response(
        content=data,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.post("/{document_id}/versions", response_model=DocumentResponse)
async def upload_document_version(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.upload_version(current_user, document_id, file)


@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentVersionResponse]:
    return await service.list_versions(current_user, document_id)
