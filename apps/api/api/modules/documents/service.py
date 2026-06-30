"""Document management service — upload, storage, versioning, duplicate detection."""

import hashlib
import logging
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_document_classification import (
    ClassificationContext,
    ClassificationResult,
)
from verdin_document_classification import (
    classify_document as run_document_classification,
)
from verdin_event_types import DocumentEventType

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.config import get_settings
from api.core.events import publish_platform_event
from api.core.job_queue import JobType, enqueue_job
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.documents.constants import (
    DocumentProcessingStatus,
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
    is_ocr_eligible,
)
from api.modules.documents.metadata_repository import DocumentMetadataRepository
from api.modules.documents.metadata_schemas import (
    DocumentEntityResolutionResponse,
    DocumentMetadataResponse,
    DocumentResolutionsResponse,
    ResolutionConfirmRequest,
    ResolutionRejectRequest,
)
from api.modules.documents.metadata_service import run_entity_resolution, run_metadata_extraction
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.permissions import (
    DOCUMENT_DELETE_ROLE,
    DOCUMENT_WRITE_ROLE,
)
from api.modules.documents.repository import DocumentListFilters, DocumentRepository
from api.modules.documents.schemas import (
    DocumentClassificationResponse,
    DocumentListParams,
    DocumentOcrResponse,
    DocumentParsedCreditReportResponse,
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
from api.modules.timeline.builders import (
    document_pipeline_event,
    document_uploaded_event,
    document_version_created_event,
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
        metadata_repo: DocumentMetadataRepository,
        storage: DocumentStorage,
        session: AsyncSession | None = None,
    ) -> None:
        self._documents = document_repo
        self._cases = case_repo
        self._accounts = account_repo
        self._metadata = metadata_repo
        self._storage = storage
        self._session = session

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
            DocumentMetadataRepository(session),
            storage or get_document_storage(),
            session=session,
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
        base_name = file_name.replace("\\", "/").split("/")[-1].strip()
        safe_name = "".join(
            char if char.isalnum() or char in {".", "-", "_"} else "_" for char in base_name
        ).lstrip(".")
        safe_name = safe_name or "document"
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
            metadata_status=params.metadata_status,
            resolution_status=params.resolution_status,
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

        # Commit before enqueuing async work. The worker reads the document on a
        # separate connection and may dequeue the OCR job before this request's
        # transaction commits — a read-after-write race that otherwise drops the
        # job and leaves the document stuck in "queued".
        if self._session is not None:
            await self._session.commit()

        self._queue_ocr_job(document)
        await self._documents.update(document)
        if self._session is not None:
            await publish_platform_event(self._session, document_uploaded_event(document, user.id))

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
        document.ocr_error = None
        document.ocr_processed_at = None
        document.ocr_version_number = None
        document.document_type = None
        document.confidence_score = None
        document.classification_method = None
        document.classified_at = None
        document.classified_by_id = None
        self._apply_initial_processing_status(document)
        apply_audit_on_update(document, user.id)
        updated = await self._documents.update(document)

        # See upload_document: persist the new version before enqueuing OCR so
        # the worker never races the request transaction.
        if self._session is not None:
            await self._session.commit()

        self._queue_ocr_job(updated)
        updated = await self._documents.update(updated)
        if self._session is not None:
            await publish_platform_event(
                self._session, document_version_created_event(updated, user.id)
            )
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
        document.document_type = None
        document.confidence_score = None
        document.classification_method = None
        document.classified_at = None
        document.classified_by_id = None
        self._apply_initial_processing_status(document)
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)

        self._queue_ocr_job(document)
        await self._documents.update(document)
        return DocumentOcrResponse.from_model(document)

    def _build_classification_context(self, document: Document) -> ClassificationContext:
        return ClassificationContext(
            ocr_text=document.ocr_text,
            file_name=document.file_name,
            title=document.title,
            mime_type=document.mime_type,
        )

    def _apply_classification_result(
        self,
        document: Document,
        result: ClassificationResult,
        *,
        classified_by_id: uuid.UUID | None,
    ) -> None:
        document.document_type = result.document_type.value
        document.confidence_score = result.confidence_score
        document.classification_method = result.classification_method.value
        document.classified_at = datetime.now(UTC)
        document.classified_by_id = classified_by_id

    def _queue_classify_job(self, document: Document) -> None:
        settings = get_settings()
        if not settings.document_classification_enabled:
            return
        try:
            enqueue_job(JobType.DOCUMENT_CLASSIFY, {"document_id": str(document.id)})
        except Exception:
            logger.exception("Failed to enqueue classification job for document %s", document.id)

    async def classify_document(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentClassificationResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)

        result = run_document_classification(self._build_classification_context(document))
        self._apply_classification_result(document, result, classified_by_id=user.id)
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)
        self._queue_metadata_extract_job(document)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                document_pipeline_event(
                    document,
                    DocumentEventType.CLASSIFICATION_COMPLETED,
                    title="Classification completed",
                    description=f"Document classified as {result.document_type.value}.",
                    performed_by=user.id,
                    metadata={
                        "document_type": result.document_type.value,
                        "confidence_score": result.confidence_score,
                    },
                ),
            )
        return DocumentClassificationResponse.from_model(document)

    async def get_classification(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentClassificationResponse:
        document = await self._get_document_for_user(document_id, user)
        return DocumentClassificationResponse.from_model(document)

    async def get_parsed_credit_report(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentParsedCreditReportResponse:
        document = await self._get_document_for_user(document_id, user)
        parsed_report = await self._documents.get_parsed_credit_report(
            document.id,
            organization_id=document.organization_id,
        )
        if parsed_report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed credit report not found",
            )
        return DocumentParsedCreditReportResponse.from_model(parsed_report)

    def _queue_metadata_extract_job(self, document: Document) -> None:
        settings = get_settings()
        if not settings.document_metadata_enabled:
            return
        try:
            enqueue_job(JobType.DOCUMENT_METADATA_EXTRACT, {"document_id": str(document.id)})
        except Exception:
            logger.exception("Failed to enqueue metadata extraction for document %s", document.id)

    async def get_metadata(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentMetadataResponse:
        document = await self._get_document_for_user(document_id, user)
        metadata = await self._metadata.get_metadata_by_document(
            document.id,
            organization_id=document.organization_id,
        )
        if metadata is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document metadata not found",
            )
        return DocumentMetadataResponse.from_model(metadata)

    def _queue_entity_resolve_job(self, document: Document) -> None:
        settings = get_settings()
        if not settings.document_entity_resolution_enabled:
            return
        try:
            enqueue_job(JobType.DOCUMENT_ENTITY_RESOLVE, {"document_id": str(document.id)})
        except Exception:
            logger.exception("Failed to enqueue entity resolution for document %s", document.id)

    async def extract_metadata(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentMetadataResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)
        if not document.ocr_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="OCR text is required before metadata extraction",
            )
        response = await run_metadata_extraction(document, self._metadata)
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)
        self._queue_entity_resolve_job(document)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                document_pipeline_event(
                    document,
                    DocumentEventType.METADATA_EXTRACTED,
                    title="Metadata extracted",
                    description=f"Structured metadata extracted from '{document.title}'.",
                    performed_by=user.id,
                    metadata={"confidence_score": response.confidence_score},
                ),
            )
        return response

    async def get_resolutions(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentResolutionsResponse:
        document = await self._get_document_for_user(document_id, user)
        rows = await self._metadata.list_resolutions(
            document.id,
            organization_id=document.organization_id,
        )
        return DocumentResolutionsResponse(
            document_id=document.id,
            resolutions=[DocumentEntityResolutionResponse.from_model(row) for row in rows],
        )

    async def resolve_entities(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentResolutionsResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)
        try:
            response = await run_entity_resolution(
                document,
                self._metadata,
                self._cases,
                self._accounts,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)
        if self._session is not None:
            account_match = next(
                (row for row in response.resolutions if row.entity_type.value == "account"),
                None,
            )
            await publish_platform_event(
                self._session,
                document_pipeline_event(
                    document,
                    DocumentEventType.ENTITY_RESOLVED,
                    title="Entity resolution completed",
                    description="Document entities were resolved to case and account records.",
                    performed_by=user.id,
                    metadata={
                        "resolution_count": len(response.resolutions),
                        "account_status": (
                            account_match.resolution_status.value if account_match else None
                        ),
                    },
                ),
            )
        return response

    async def confirm_resolution(
        self,
        user: User,
        document_id: uuid.UUID,
        resolution_id: uuid.UUID,
        body: ResolutionConfirmRequest,
    ) -> DocumentResolutionsResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)
        resolution = await self._metadata.get_resolution(
            resolution_id,
            organization_id=document.organization_id,
        )
        if resolution is None or resolution.document_id != document.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found"
            )

        if resolution.resolution_status == ResolutionStatus.AMBIGUOUS.value:
            if body.matched_entity_id is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="matched_entity_id is required for ambiguous resolutions",
                )
            resolution.matched_entity_id = body.matched_entity_id
        elif resolution.matched_entity_id is None and body.matched_entity_id is not None:
            resolution.matched_entity_id = body.matched_entity_id

        resolution.resolution_status = ResolutionStatus.CONFIRMED.value
        resolution.resolution_method = ResolutionMethod.MANUAL.value
        resolution.reviewed_at = datetime.now(UTC)
        resolution.reviewed_by_id = user.id
        await self._metadata.update_resolution(resolution)

        if (
            resolution.entity_type == MatchedEntityType.ACCOUNT.value
            and resolution.matched_entity_id is not None
        ):
            document.account_id = resolution.matched_entity_id
            apply_audit_on_update(document, user.id)
            await self._documents.update(document)

        return await self.get_resolutions(user, document_id)

    async def reject_resolution(
        self,
        user: User,
        document_id: uuid.UUID,
        resolution_id: uuid.UUID,
        body: ResolutionRejectRequest,
    ) -> DocumentResolutionsResponse:
        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)
        resolution = await self._metadata.get_resolution(
            resolution_id,
            organization_id=document.organization_id,
        )
        if resolution is None or resolution.document_id != document.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found"
            )

        resolution.resolution_status = ResolutionStatus.REJECTED.value
        resolution.resolution_method = ResolutionMethod.MANUAL.value
        resolution.matched_entity_id = None
        resolution.reasoning = body.reason or resolution.reasoning
        resolution.reviewed_at = datetime.now(UTC)
        resolution.reviewed_by_id = user.id
        await self._metadata.update_resolution(resolution)
        return await self.get_resolutions(user, document_id)
