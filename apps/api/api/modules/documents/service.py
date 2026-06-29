"""Document management service — upload, storage, versioning, duplicate detection."""

import hashlib
import logging
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.config import get_settings
from api.core.job_queue import JobType, enqueue_job
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.documents.constants import DocumentProcessingStatus, is_ocr_eligible
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.permissions import (
    DOCUMENT_DELETE_ROLE,
    DOCUMENT_WRITE_ROLE,
)
from api.modules.documents.repository import DocumentListFilters, DocumentRepository
from api.modules.documents.schemas import (
    DocumentListParams,
    DocumentOcrResponse,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionResponse,
)
from api.modules.documents.storage import (
    DocumentStorage,
    async_get,
    async_put,
    get_document_storage,
)
from api.repositories.document import DocumentRepositoryProtocol

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
)


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepositoryProtocol,
        case_repo: CaseRepository,
        account_repo: AccountRepository,
        storage: DocumentStorage,
    ) -> None:
        self._documents = document_repo
        self._cases = case_repo
        self._accounts = account_repo
        self._storage = storage

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        storage: DocumentStorage | None = None,
    ) -> "DocumentService":
        return cls(
            DocumentRepository(session),
            CaseRepository(session),
            AccountRepository(session),
            storage or get_document_storage(),
        )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, DOCUMENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify documents",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, DOCUMENT_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete documents",
            )

    async def _validate_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case must belong to the same organization",
            )

    async def _validate_account(
        self,
        account_id: uuid.UUID | None,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> None:
        if account_id is None:
            return
        account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
        if account is None or account.case_id != case_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Account must belong to the same case and organization",
            )

    async def _read_upload(self, file: UploadFile) -> tuple[bytes, str]:
        settings = get_settings()
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported file type: {content_type}",
            )

        data = await file.read()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty",
            )
        if len(data) > settings.document_max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds maximum upload size",
            )
        return data, content_type

    @staticmethod
    def _compute_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _storage_key(
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        document_id: uuid.UUID,
        version_number: int,
        file_name: str,
    ) -> str:
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        return f"{organization_id}/{case_id}/{document_id}/v{version_number}/{safe_name}"

    async def _get_document_for_user(
        self,
        document_id: uuid.UUID,
        user: User,
        *,
        include_versions: bool = False,
    ) -> Document:
        organization_id = self._require_organization(user)
        document = await self._documents.get_by_id(
            document_id,
            organization_id=organization_id,
            include_versions=include_versions,
        )
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document

    @staticmethod
    def _filters_from_params(
        organization_id: uuid.UUID,
        params: DocumentListParams,
    ) -> DocumentListFilters:
        return DocumentListFilters(
            organization_id=organization_id,
            search=params.search,
            case_id=params.case_id,
            account_id=params.account_id,
            is_duplicate=params.is_duplicate,
            processing_status=params.processing_status,
            skip=params.offset,
            limit=params.page_size,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )

    def _apply_initial_processing_status(self, document: Document) -> None:
        if not is_ocr_eligible(document.mime_type):
            document.processing_status = DocumentProcessingStatus.SKIPPED.value
            return
        document.processing_status = DocumentProcessingStatus.PENDING.value

    def _queue_ocr_job(self, document: Document) -> None:
        settings = get_settings()
        if not settings.document_ocr_enabled:
            return
        if not is_ocr_eligible(document.mime_type):
            return

        try:
            message = enqueue_job(
                JobType.OCR,
                {
                    "document_id": str(document.id),
                    "version_number": document.version_number,
                },
            )
            document.processing_status = DocumentProcessingStatus.QUEUED.value
            document.ocr_job_id = message.job_id
            document.ocr_error = None
        except Exception:
            logger.exception("Failed to enqueue OCR job for document %s", document.id)
            document.processing_status = DocumentProcessingStatus.PENDING.value

    async def upload_document(
        self,
        user: User,
        *,
        file: UploadFile,
        title: str,
        case_id: uuid.UUID,
        description: str | None = None,
        account_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        await self._validate_account(account_id, organization_id, case_id)

        data, content_type = await self._read_upload(file)
        file_hash = self._compute_hash(data)
        file_name = file.filename or "upload.bin"

        existing = await self._documents.find_by_hash(organization_id, file_hash)
        is_duplicate = existing is not None
        duplicate_of_id = existing.id if existing else None

        document_id = uuid.uuid4()
        storage_key = self._storage_key(organization_id, case_id, document_id, 1, file_name)
        await async_put(self._storage, storage_key, data, content_type)

        now = datetime.now(UTC)
        document = Document(
            id=document_id,
            organization_id=organization_id,
            case_id=case_id,
            account_id=account_id,
            title=title,
            description=description,
            file_name=file_name,
            storage_key=storage_key,
            mime_type=content_type,
            file_size=len(data),
            file_hash=file_hash,
            version_number=1,
            is_duplicate=is_duplicate,
            duplicate_of_id=duplicate_of_id,
        )
        apply_audit_on_create(document, user.id)
        self._apply_initial_processing_status(document)
        await self._documents.create(document)

        version = DocumentVersion(
            id=uuid.uuid4(),
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            file_hash=file_hash,
            file_name=file_name,
            mime_type=content_type,
            file_size=len(data),
            created_at=now,
            created_by_id=user.id,
        )
        await self._documents.create_version(version)

        self._queue_ocr_job(document)
        await self._documents.update(document)

        return DocumentResponse.from_model(document)

    async def upload_version(
        self,
        user: User,
        document_id: uuid.UUID,
        file: UploadFile,
    ) -> DocumentResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)

        data, content_type = await self._read_upload(file)
        file_hash = self._compute_hash(data)
        file_name = file.filename or document.file_name
        new_version_number = document.version_number + 1

        storage_key = self._storage_key(
            document.organization_id,
            document.case_id,
            document.id,
            new_version_number,
            file_name,
        )
        await async_put(self._storage, storage_key, data, content_type)

        now = datetime.now(UTC)
        version = DocumentVersion(
            id=uuid.uuid4(),
            document_id=document.id,
            version_number=new_version_number,
            storage_key=storage_key,
            file_hash=file_hash,
            file_name=file_name,
            mime_type=content_type,
            file_size=len(data),
            created_at=now,
            created_by_id=user.id,
        )
        await self._documents.create_version(version)

        document.file_name = file_name
        document.storage_key = storage_key
        document.mime_type = content_type
        document.file_size = len(data)
        document.file_hash = file_hash
        document.version_number = new_version_number
        document.ocr_text = None
        document.ocr_processed_at = None
        document.ocr_version_number = None
        self._apply_initial_processing_status(document)
        apply_audit_on_update(document, user.id)
        updated = await self._documents.update(document)

        self._queue_ocr_job(updated)
        updated = await self._documents.update(updated)
        return DocumentResponse.from_model(updated)

    async def list_documents(
        self,
        user: User,
        params: DocumentListParams,
    ) -> PaginatedResponse[DocumentResponse]:
        organization_id = self._require_organization(user)
        filters = self._filters_from_params(organization_id, params)
        items, total = await self._documents.list_documents(filters)
        return paginate(
            [DocumentResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_document(self, user: User, document_id: uuid.UUID) -> DocumentResponse:
        document = await self._get_document_for_user(document_id, user, include_versions=True)
        return DocumentResponse.from_model(document, include_versions=True)

    async def update_document(
        self,
        user: User,
        document_id: uuid.UUID,
        data: DocumentUpdate,
    ) -> DocumentResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        document = await self._get_document_for_user(document_id, user)

        update_data = data.model_dump(exclude_unset=True)
        if "account_id" in update_data:
            await self._validate_account(
                update_data.get("account_id"),
                organization_id,
                document.case_id,
            )

        for field, value in update_data.items():
            setattr(document, field, value)

        apply_audit_on_update(document, user.id)
        updated = await self._documents.update(document)
        return DocumentResponse.from_model(updated)

    async def delete_document(self, user: User, document_id: uuid.UUID) -> None:
        self._require_delete(user)
        document = await self._get_document_for_user(document_id, user)
        document.soft_delete()
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)

    async def download_document(
        self,
        user: User,
        document_id: uuid.UUID,
        *,
        version_number: int | None = None,
    ) -> tuple[bytes, str, str]:
        document = await self._get_document_for_user(document_id, user)
        storage_key = document.storage_key
        file_name = document.file_name
        mime_type = document.mime_type or "application/octet-stream"

        if version_number is not None and version_number != document.version_number:
            versions = await self._documents.list_versions(document.id)
            match = next((v for v in versions if v.version_number == version_number), None)
            if match is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document version not found",
                )
            storage_key = match.storage_key
            file_name = match.file_name
            mime_type = match.mime_type or mime_type

        data = await async_get(self._storage, storage_key)
        return data, file_name, mime_type

    async def list_versions(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> list[DocumentVersionResponse]:
        await self._get_document_for_user(document_id, user)
        versions = await self._documents.list_versions(document_id)
        return [DocumentVersionResponse.from_model(v) for v in versions]

    async def get_ocr_result(self, user: User, document_id: uuid.UUID) -> DocumentOcrResponse:
        document = await self._get_document_for_user(document_id, user)
        return DocumentOcrResponse.from_model(document)

    async def retry_ocr(self, user: User, document_id: uuid.UUID) -> DocumentOcrResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)

        if not is_ocr_eligible(document.mime_type):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Document format is not eligible for OCR",
            )

        document.ocr_text = None
        document.ocr_error = None
        document.ocr_processed_at = None
        document.ocr_version_number = None
        self._apply_initial_processing_status(document)
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)

        self._queue_ocr_job(document)
        await self._documents.update(document)
        return DocumentOcrResponse.from_model(document)
