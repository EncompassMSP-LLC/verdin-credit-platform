"""Document management service — upload, storage, versioning, duplicate detection."""

import hashlib
import logging
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any, Literal

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
from api.modules.documents.cross_bureau_comparison import (
    CrossBureauComparisonResult,
    compare_cross_bureau_reports,
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
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from api.modules.documents.permissions import (
    DOCUMENT_DELETE_ROLE,
    DOCUMENT_WRITE_ROLE,
)
from api.modules.documents.repository import DocumentListFilters, DocumentRepository
from api.modules.documents.schemas import (
    BureauTradelineSnapshotResponse,
    CaseComplianceEvidenceLinksResponse,
    CaseCreditReportDiscrepanciesResponse,
    CaseFcraFindingsResponse,
    CaseMetro2FindingsResponse,
    CaseTradelineChronologyResponse,
    ComplianceEvidenceExhibitLink,
    ComplianceEvidenceLinkItem,
    ComplianceEvidenceReportLink,
    ComplianceEvidenceSummary,
    CrossBureauComparisonSummary,
    CrossBureauDiscrepancyResponse,
    CrossBureauPossibleCauseResponse,
    DocumentClassificationResponse,
    DocumentDuplicateGroupResponse,
    DocumentFcraFindingsResponse,
    DocumentListParams,
    DocumentMetro2FindingsResponse,
    DocumentOcrResponse,
    DocumentParsedCreditReportAccountCandidatesResponse,
    DocumentParsedCreditReportComparisonResponse,
    DocumentParsedCreditReportResponse,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionResponse,
    FcraFindingResponse,
    FcraFindingSummary,
    ImportedParsedReportAccountItem,
    ImportParsedReportAccountsRequest,
    ImportParsedReportAccountsResponse,
    Metro2FindingResponse,
    Metro2FindingSummary,
    ParsedReportAccountCandidate,
    ParsedReportAccountChange,
    ParsedReportComparisonSummary,
    ParsedReportFieldDiff,
    PrepareCreditReportDisputesRequest,
    PrepareCreditReportDisputesResponse,
    PreparedCreditReportDisputeItem,
    TradelineChronologyEventResponse,
    TradelineChronologyItemResponse,
    TradelineChronologySnapshotResponse,
    TradelineChronologySummary,
)
from api.modules.documents.storage import (
    DocumentStorage,
    async_get,
    async_put,
    get_document_storage,
)
from api.modules.tasks.models import Task, TaskPriority
from api.modules.tasks.repository import TaskRepository
from api.modules.tasks.schemas import TaskResponse
from api.modules.timeline.builders import (
    document_pipeline_event,
    document_uploaded_event,
    document_version_created_event,
    portal_document_uploaded_event,
    task_created_event,
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
PARSED_REPORT_REVIEW_TASK_SOURCE = "documents.parsed_credit_report"
_TRADELINE_COMPARE_FIELDS: tuple[str, ...] = (
    "balance",
    "past_due_amount",
    "payment_status",
    "account_status",
    "high_credit",
    "credit_limit",
    "open_date",
    "date_closed",
    "date_reported",
    "date_first_delinquency",
    "remarks",
    "payment_history",
)


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepositoryProtocol,
        case_repo: CaseRepository,
        account_repo: AccountRepository,
        metadata_repo: DocumentMetadataRepository,
        storage: DocumentStorage,
        task_repo: TaskRepository | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self._documents = document_repo
        self._cases = case_repo
        self._accounts = account_repo
        self._metadata = metadata_repo
        self._storage = storage
        self._tasks = task_repo
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
            TaskRepository(session),
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

    async def upload_identity_document(
        self,
        user: User,
        *,
        case_id: uuid.UUID,
        file: UploadFile,
        title: str | None = None,
        client_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        """Upload a government ID copy and link it to the case (and linked client)."""
        from api.modules.clients.models import Client
        from api.modules.documents.constants import DocumentType

        self._require_write(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )
        organization_id = self._require_organization(user)
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        if client_id is not None and case.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case does not belong to this client",
            )

        document_title = title or "Driver's license"
        response = await self.upload_document(
            user,
            file=file,
            title=document_title,
            case_id=case_id,
            description="Government-issued photo ID for dispute mail packets",
        )

        document = await self._documents.get_by_id(
            response.id,
            organization_id=organization_id,
        )
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Uploaded identity document could not be loaded",
            )

        document.document_type = DocumentType.IDENTITY_DOCUMENT.value
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)

        case.identity_document_id = document.id
        apply_audit_on_update(case, user.id)
        await self._cases.update(case)

        if case.client_id is not None:
            client = await self._session.get(Client, case.client_id)
            if client is not None and client.organization_id == organization_id:
                client.identity_document_id = document.id
                apply_audit_on_update(client, user.id)

        await self._session.commit()

        return DocumentResponse.from_model(document)

    async def upload_proof_of_address_document(
        self,
        user: User,
        *,
        case_id: uuid.UUID,
        file: UploadFile,
        title: str | None = None,
        client_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        """Upload proof of mailing address and link it to the case (and linked client)."""
        from api.modules.clients.models import Client
        from api.modules.documents.constants import DocumentType

        self._require_write(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )
        organization_id = self._require_organization(user)
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        if client_id is not None and case.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case does not belong to this client",
            )

        document_title = title or "Proof of mailing address"
        response = await self.upload_document(
            user,
            file=file,
            title=document_title,
            case_id=case_id,
            description="Proof of current mailing address for dispute mail packets",
        )

        document = await self._documents.get_by_id(
            response.id,
            organization_id=organization_id,
        )
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Uploaded proof-of-address document could not be loaded",
            )

        document.document_type = DocumentType.PROOF_OF_ADDRESS.value
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)

        case.proof_of_address_document_id = document.id
        apply_audit_on_update(case, user.id)
        await self._cases.update(case)

        if case.client_id is not None:
            client = await self._session.get(Client, case.client_id)
            if client is not None and client.organization_id == organization_id:
                client.proof_of_address_document_id = document.id
                apply_audit_on_update(client, user.id)

        await self._session.commit()

        return DocumentResponse.from_model(document)

    async def upload_signed_consent_document(
        self,
        user: User,
        *,
        case_id: uuid.UUID,
        file: UploadFile,
        consent_type: str,
        title: str | None = None,
        client_id: uuid.UUID | None = None,
    ) -> DocumentResponse:
        """Upload a signed consent form and tag it for compliance records."""
        from api.modules.documents.constants import DocumentType

        self._require_write(user)
        organization_id = self._require_organization(user)
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        if client_id is not None and case.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case does not belong to this client",
            )

        document_title = title or f"Signed consent — {consent_type.replace('_', ' ')}"
        response = await self.upload_document(
            user,
            file=file,
            title=document_title,
            case_id=case_id,
            description="Signed client consent form",
        )

        document = await self._documents.get_by_id(
            response.id,
            organization_id=organization_id,
        )
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Uploaded consent document could not be loaded",
            )

        document.document_type = DocumentType.SIGNED_CONSENT.value
        apply_audit_on_update(document, user.id)
        await self._documents.update(document)

        if self._session is not None:
            await self._session.commit()

        return DocumentResponse.from_model(document)

    async def upload_portal_consent_document(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
        case_id: uuid.UUID,
        file: UploadFile,
        consent_type: str,
        title: str,
    ) -> Document:
        from api.modules.documents.constants import DocumentType

        await self._validate_case(case_id, organization_id)

        data, content_type = await self._read_upload(file)
        file_hash = self._compute_hash(data)
        file_name = file.filename or "consent-signature.png"

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
            account_id=None,
            title=title,
            description=f"Portal consent signature for {consent_type}",
            file_name=file_name,
            storage_key=storage_key,
            mime_type=content_type,
            file_size=len(data),
            file_hash=file_hash,
            version_number=1,
            is_duplicate=is_duplicate,
            duplicate_of_id=duplicate_of_id,
            document_type=DocumentType.SIGNED_CONSENT.value,
        )
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
            created_by_id=portal_user_id,
        )
        await self._documents.create_version(version)

        if self._session is not None:
            await self._session.commit()

        self._queue_ocr_job(document)
        await self._documents.update(document)
        return document

    async def store_generated_consent_pdf(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        created_by_id: uuid.UUID,
        title: str,
        pdf_bytes: bytes,
        template_key: str,
        description: str | None = None,
    ) -> Document:
        from api.modules.documents.constants import DocumentType

        await self._validate_case(case_id, organization_id)

        content_type = "application/pdf"
        file_hash = self._compute_hash(pdf_bytes)
        file_name = f"signed-consent-{template_key}.pdf"

        existing = await self._documents.find_by_hash(organization_id, file_hash)
        is_duplicate = existing is not None
        duplicate_of_id = existing.id if existing else None

        document_id = uuid.uuid4()
        storage_key = self._storage_key(organization_id, case_id, document_id, 1, file_name)
        await async_put(self._storage, storage_key, pdf_bytes, content_type)

        now = datetime.now(UTC)
        document = Document(
            id=document_id,
            organization_id=organization_id,
            case_id=case_id,
            account_id=None,
            title=title,
            description=description or f"Signed consent document ({template_key})",
            file_name=file_name,
            storage_key=storage_key,
            mime_type=content_type,
            file_size=len(pdf_bytes),
            file_hash=file_hash,
            version_number=1,
            is_duplicate=is_duplicate,
            duplicate_of_id=duplicate_of_id,
            document_type=DocumentType.SIGNED_CONSENT.value,
        )
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
            file_size=len(pdf_bytes),
            created_at=now,
            created_by_id=created_by_id,
        )
        await self._documents.create_version(version)

        if self._session is not None:
            await self._session.commit()

        self._queue_ocr_job(document)
        await self._documents.update(document)
        return document

    async def upload_document_for_portal(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
        case_id: uuid.UUID,
        file: UploadFile,
        title: str,
        description: str | None = None,
    ) -> Document:
        await self._validate_case(case_id, organization_id)

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
            account_id=None,
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
            created_by_id=portal_user_id,
        )
        await self._documents.create_version(version)

        if self._session is not None:
            await self._session.commit()

        self._queue_ocr_job(document)
        await self._documents.update(document)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                portal_document_uploaded_event(document, portal_user_id=portal_user_id),
            )

        return document

    async def list_documents_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[Document]:
        documents, _total = await self._documents.list_documents(
            DocumentListFilters(
                organization_id=organization_id,
                case_id=case_id,
                skip=0,
                limit=100,
                sort_by="created_at",
                sort_order="desc",
            )
        )
        return documents

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

    async def get_duplicate_group(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentDuplicateGroupResponse:
        document = await self._get_document_for_user(document_id, user)
        canonical_id = document.duplicate_of_id or document.id
        group = await self._documents.list_duplicate_group(document.organization_id, canonical_id)
        canonical = next((item for item in group if item.id == canonical_id), None)
        if canonical is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canonical duplicate document not found",
            )
        duplicates = [item for item in group if item.id != canonical.id]
        return DocumentDuplicateGroupResponse.from_group(
            document_id=document.id,
            canonical_document=canonical,
            duplicate_documents=duplicates,
        )

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

    @staticmethod
    def _string_or_none(value: object) -> str | None:
        return value.strip() if isinstance(value, str) and value.strip() else None

    @staticmethod
    def _float_or_none(value: object) -> float | None:
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace(",", "").replace("$", ""))
            except ValueError:
                return None
        return None

    @classmethod
    def _account_key(cls, account: dict[str, Any], fallback_index: int) -> str:
        account_number = cls._string_or_none(account.get("account_number_masked"))
        creditor = (cls._string_or_none(account.get("creditor_name")) or "unknown").lower()
        if account_number:
            return f"{creditor}:{account_number.lower()}"
        return f"{creditor}:row-{fallback_index}"

    @classmethod
    def _field_value_for_diff(
        cls, account: dict[str, Any] | None, field_name: str
    ) -> str | float | None:
        if account is None:
            return None
        if field_name in {"balance", "past_due_amount", "high_credit", "credit_limit"}:
            return cls._float_or_none(account.get(field_name))
        return cls._string_or_none(account.get(field_name))

    @classmethod
    def _account_field_diffs(
        cls,
        *,
        previous: dict[str, Any] | None,
        current: dict[str, Any] | None,
    ) -> list[ParsedReportFieldDiff]:
        if previous is None or current is None:
            return []
        diffs: list[ParsedReportFieldDiff] = []
        for field_name in _TRADELINE_COMPARE_FIELDS:
            previous_value = cls._field_value_for_diff(previous, field_name)
            current_value = cls._field_value_for_diff(current, field_name)
            if previous_value != current_value:
                diffs.append(
                    ParsedReportFieldDiff(
                        field=field_name,
                        previous=previous_value,
                        current=current_value,
                    )
                )
        return diffs

    @classmethod
    def _account_change(
        cls,
        *,
        match_key: str,
        previous: dict[str, Any] | None,
        current: dict[str, Any] | None,
    ) -> ParsedReportAccountChange:
        baseline = current or previous or {}
        previous_balance = cls._float_or_none(previous.get("balance")) if previous else None
        current_balance = cls._float_or_none(current.get("balance")) if current else None
        balance_delta = (
            round(current_balance - previous_balance, 2)
            if current_balance is not None and previous_balance is not None
            else None
        )
        previous_status = cls._string_or_none(previous.get("payment_status")) if previous else None
        current_status = cls._string_or_none(current.get("payment_status")) if current else None
        field_diffs = cls._account_field_diffs(previous=previous, current=current)

        change_type: Literal["added", "removed", "changed", "unchanged"]
        if previous is None:
            change_type = "added"
        elif current is None:
            change_type = "removed"
        elif field_diffs:
            change_type = "changed"
        else:
            change_type = "unchanged"

        return ParsedReportAccountChange(
            match_key=match_key,
            creditor_name=cls._string_or_none(baseline.get("creditor_name")),
            account_number_masked=cls._string_or_none(baseline.get("account_number_masked")),
            change_type=change_type,
            previous_balance=previous_balance,
            current_balance=current_balance,
            balance_delta=balance_delta,
            previous_payment_status=previous_status,
            current_payment_status=current_status,
            field_diffs=field_diffs,
        )

    @classmethod
    def _accounts_by_key(cls, parsed_report: dict[str, object]) -> dict[str, dict[str, Any]]:
        accounts = parsed_report.get("accounts")
        if not isinstance(accounts, list):
            return {}
        keyed: dict[str, dict[str, Any]] = {}
        for index, account in enumerate(accounts):
            if isinstance(account, dict):
                keyed[cls._account_key(account, index)] = account
        return keyed

    async def compare_parsed_credit_report(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentParsedCreditReportComparisonResponse:
        document = await self._get_document_for_user(document_id, user)
        current = await self._documents.get_parsed_credit_report(
            document.id,
            organization_id=document.organization_id,
        )
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed credit report not found",
            )

        previous = await self._documents.get_previous_parsed_credit_report(
            organization_id=document.organization_id,
            case_id=document.case_id,
            bureau=current.bureau,
            before_document_id=document.id,
            before_parsed_at=current.parsed_at,
        )

        current_accounts = self._accounts_by_key(current.parsed_report)
        previous_accounts = self._accounts_by_key(previous.parsed_report) if previous else {}
        changes = [
            self._account_change(
                match_key=key,
                previous=previous_accounts.get(key),
                current=current_accounts.get(key),
            )
            for key in sorted(set(current_accounts) | set(previous_accounts))
        ]
        summary = ParsedReportComparisonSummary(
            added=sum(1 for change in changes if change.change_type == "added"),
            removed=sum(1 for change in changes if change.change_type == "removed"),
            changed=sum(1 for change in changes if change.change_type == "changed"),
            unchanged=sum(1 for change in changes if change.change_type == "unchanged"),
        )

        return DocumentParsedCreditReportComparisonResponse(
            document_id=document.id,
            bureau=current.bureau,
            previous_document_id=previous.document_id if previous else None,
            current_parsed_at=current.parsed_at,
            previous_parsed_at=previous.parsed_at if previous else None,
            summary=summary,
            account_changes=changes,
        )

    async def get_metro2_findings(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentMetro2FindingsResponse:
        document = await self._get_document_for_user(document_id, user)
        current = await self._documents.get_parsed_credit_report(
            document.id,
            organization_id=document.organization_id,
        )
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed credit report not found",
            )
        return self._metro2_document_response(
            document_id=document.id,
            bureau=current.bureau,
            schema_version=current.schema_version,
            parsed_report=current.parsed_report,
        )

    def _metro2_document_response(
        self,
        *,
        document_id: uuid.UUID,
        bureau: str,
        schema_version: str | None,
        parsed_report: dict[str, Any],
    ) -> DocumentMetro2FindingsResponse:
        from api.modules.documents.metro2_rules import evaluate_tradelines

        result = evaluate_tradelines(
            document_id=document_id,
            bureau=bureau,
            parsed_report=parsed_report,
        )
        return DocumentMetro2FindingsResponse(
            document_id=result.document_id,
            bureau=result.bureau,
            schema_version=result.schema_version or schema_version,
            summary=Metro2FindingSummary(**result.summary),
            findings=[
                Metro2FindingResponse(
                    rule_id=finding.rule_id,
                    severity=finding.severity,
                    title=finding.title,
                    description=finding.description,
                    tradeline_index=finding.tradeline_index,
                    creditor_name=finding.creditor_name,
                    account_number_masked=finding.account_number_masked,
                    fields=list(finding.fields),
                    observed=finding.observed,
                )
                for finding in result.findings
            ],
        )

    async def get_case_metro2_findings(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseMetro2FindingsResponse:
        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        parsed_reports = await self._documents.list_case_parsed_credit_reports(
            organization_id=organization_id,
            case_id=case_id,
        )
        reports_by_bureau = self._latest_parsed_reports_by_bureau(parsed_reports)
        if not reports_by_bureau:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No parsed credit reports found for this case",
            )

        documents: list[DocumentMetro2FindingsResponse] = []
        for bureau in sorted(reports_by_bureau):
            document_id, parsed_report = reports_by_bureau[bureau]
            schema_version = parsed_report.get("schema_version")
            documents.append(
                self._metro2_document_response(
                    document_id=document_id,
                    bureau=bureau,
                    schema_version=schema_version if isinstance(schema_version, str) else None,
                    parsed_report=parsed_report,
                )
            )

        summary = Metro2FindingSummary(
            total=sum(item.summary.total for item in documents),
            high=sum(item.summary.high for item in documents),
            medium=sum(item.summary.medium for item in documents),
            low=sum(item.summary.low for item in documents),
            tradelines_evaluated=sum(item.summary.tradelines_evaluated for item in documents),
        )
        return CaseMetro2FindingsResponse(
            case_id=case_id,
            reports_evaluated=sorted(reports_by_bureau),
            document_ids_by_bureau={
                bureau: document_id for bureau, (document_id, _) in reports_by_bureau.items()
            },
            summary=summary,
            documents=documents,
        )

    async def get_fcra_findings(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentFcraFindingsResponse:
        document = await self._get_document_for_user(document_id, user)
        current = await self._documents.get_parsed_credit_report(
            document.id,
            organization_id=document.organization_id,
        )
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed credit report not found",
            )
        return self._fcra_document_response(
            document_id=document.id,
            bureau=current.bureau,
            schema_version=current.schema_version,
            parsed_report=current.parsed_report,
        )

    def _fcra_document_response(
        self,
        *,
        document_id: uuid.UUID,
        bureau: str,
        schema_version: str | None,
        parsed_report: dict[str, Any],
    ) -> DocumentFcraFindingsResponse:
        from api.modules.documents.fcra_rules import evaluate_tradelines

        result = evaluate_tradelines(
            document_id=document_id,
            bureau=bureau,
            parsed_report=parsed_report,
        )
        return DocumentFcraFindingsResponse(
            document_id=result.document_id,
            bureau=result.bureau,
            schema_version=result.schema_version or schema_version,
            as_of_date=result.as_of_date,
            summary=FcraFindingSummary(**result.summary),
            findings=[
                FcraFindingResponse(
                    rule_id=finding.rule_id,
                    severity=finding.severity,
                    title=finding.title,
                    description=finding.description,
                    fcra_sections=list(finding.fcra_sections),
                    tradeline_index=finding.tradeline_index,
                    creditor_name=finding.creditor_name,
                    account_number_masked=finding.account_number_masked,
                    fields=list(finding.fields),
                    observed=finding.observed,
                )
                for finding in result.findings
            ],
        )

    async def get_case_fcra_findings(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseFcraFindingsResponse:
        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        parsed_reports = await self._documents.list_case_parsed_credit_reports(
            organization_id=organization_id,
            case_id=case_id,
        )
        reports_by_bureau = self._latest_parsed_reports_by_bureau(parsed_reports)
        if not reports_by_bureau:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No parsed credit reports found for this case",
            )

        documents: list[DocumentFcraFindingsResponse] = []
        for bureau in sorted(reports_by_bureau):
            document_id, parsed_report = reports_by_bureau[bureau]
            schema_version = parsed_report.get("schema_version")
            documents.append(
                self._fcra_document_response(
                    document_id=document_id,
                    bureau=bureau,
                    schema_version=schema_version if isinstance(schema_version, str) else None,
                    parsed_report=parsed_report,
                )
            )

        summary = FcraFindingSummary(
            total=sum(item.summary.total for item in documents),
            high=sum(item.summary.high for item in documents),
            medium=sum(item.summary.medium for item in documents),
            low=sum(item.summary.low for item in documents),
            tradelines_evaluated=sum(item.summary.tradelines_evaluated for item in documents),
        )
        return CaseFcraFindingsResponse(
            case_id=case_id,
            reports_evaluated=sorted(reports_by_bureau),
            document_ids_by_bureau={
                bureau: document_id for bureau, (document_id, _) in reports_by_bureau.items()
            },
            summary=summary,
            documents=documents,
        )

    async def get_case_tradeline_chronology(
        self,
        user: User,
        case_id: uuid.UUID,
        *,
        bureau: str | None = None,
    ) -> CaseTradelineChronologyResponse:
        from api.modules.documents.tradeline_chronology import (
            ReportSnapshotInput,
            build_case_tradeline_chronology,
        )

        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        parsed_reports = await self._documents.list_case_parsed_credit_reports(
            organization_id=organization_id,
            case_id=case_id,
        )
        if not parsed_reports:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No parsed credit reports found for this case",
            )

        result = build_case_tradeline_chronology(
            case_id=case_id,
            reports=[
                ReportSnapshotInput(
                    document_id=item.document_id,
                    bureau=str(item.bureau),
                    parsed_at=item.parsed_at,
                    parsed_report=item.parsed_report,
                )
                for item in parsed_reports
            ],
            bureau=bureau,
        )
        return CaseTradelineChronologyResponse(
            case_id=result.case_id,
            reports_evaluated=result.reports_evaluated,
            bureaus=list(result.bureaus),
            summary=TradelineChronologySummary(**result.summary),
            tradelines=[
                TradelineChronologyItemResponse(
                    match_key=item.match_key,
                    bureau=item.bureau,
                    creditor_name=item.creditor_name,
                    account_number_masked=item.account_number_masked,
                    snapshot_count=item.snapshot_count,
                    event_count=item.event_count,
                    snapshots=[
                        TradelineChronologySnapshotResponse(
                            document_id=snap.document_id,
                            parsed_at=snap.parsed_at,
                            as_of_date=snap.as_of_date,
                            present=snap.present,
                            creditor_name=snap.creditor_name,
                            account_number_masked=snap.account_number_masked,
                            balance=snap.balance,
                            past_due_amount=snap.past_due_amount,
                            account_status=snap.account_status,
                            payment_status=snap.payment_status,
                            date_first_delinquency=snap.date_first_delinquency,
                            date_closed=snap.date_closed,
                            remarks=snap.remarks,
                            high_credit=snap.high_credit,
                            credit_limit=snap.credit_limit,
                        )
                        for snap in item.snapshots
                    ],
                    events=[
                        TradelineChronologyEventResponse(
                            event_type=event.event_type,
                            severity=event.severity,
                            field=event.field,
                            from_document_id=event.from_document_id,
                            to_document_id=event.to_document_id,
                            from_parsed_at=event.from_parsed_at,
                            to_parsed_at=event.to_parsed_at,
                            previous=event.previous,
                            current=event.current,
                            summary=event.summary,
                        )
                        for event in item.events
                    ],
                )
                for item in result.tradelines
            ],
        )

    async def get_case_compliance_evidence_links(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseComplianceEvidenceLinksResponse:
        from api.modules.documents.constants import DocumentType
        from api.modules.documents.evidence_links import (
            ExhibitInput,
            build_case_compliance_evidence_links,
        )

        organization_id = self._require_organization(user)
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        metro2 = await self.get_case_metro2_findings(user, case_id)
        fcra = await self.get_case_fcra_findings(user, case_id)

        exhibits: list[ExhibitInput] = []
        if case.identity_document_id is not None:
            exhibits.append(
                ExhibitInput(
                    document_id=case.identity_document_id,
                    document_type=DocumentType.IDENTITY_DOCUMENT.value,
                    role="identity",
                    label="Government-issued photo ID",
                )
            )
        if case.proof_of_address_document_id is not None:
            exhibits.append(
                ExhibitInput(
                    document_id=case.proof_of_address_document_id,
                    document_type=DocumentType.PROOF_OF_ADDRESS.value,
                    role="proof_of_address",
                    label="Proof of address",
                )
            )

        supporting_docs, _total = await self._documents.list_documents(
            DocumentListFilters(
                organization_id=organization_id,
                case_id=case_id,
                skip=0,
                limit=50,
                sort_by="created_at",
                sort_order="desc",
            )
        )
        for document in supporting_docs:
            doc_type = str(document.document_type or "")
            if doc_type in {
                DocumentType.COLLECTION_LETTER.value,
                DocumentType.BUREAU_RESPONSE.value,
                DocumentType.COURT_RECORD.value,
            }:
                if any(item.document_id == document.id for item in exhibits):
                    continue
                exhibits.append(
                    ExhibitInput(
                        document_id=document.id,
                        document_type=doc_type,
                        role="suggested",
                        label=document.title or document.file_name or doc_type,
                    )
                )

        def _document_payload(
            doc: DocumentMetro2FindingsResponse | DocumentFcraFindingsResponse,
        ) -> dict[str, Any]:
            return {
                "document_id": doc.document_id,
                "bureau": doc.bureau,
                "findings": [
                    {
                        "rule_id": finding.rule_id,
                        "severity": finding.severity,
                        "title": finding.title,
                        "tradeline_index": finding.tradeline_index,
                        "creditor_name": finding.creditor_name,
                        "account_number_masked": finding.account_number_masked,
                    }
                    for finding in doc.findings
                ],
            }

        result = build_case_compliance_evidence_links(
            case_id=case_id,
            metro2_documents=[_document_payload(doc) for doc in metro2.documents],
            fcra_documents=[_document_payload(doc) for doc in fcra.documents],
            exhibits=exhibits,
            page_lookup=None,
        )
        return CaseComplianceEvidenceLinksResponse(
            case_id=result.case_id,
            summary=ComplianceEvidenceSummary(**result.summary),
            items=[
                ComplianceEvidenceLinkItem(
                    source_kind=item.source_kind,
                    source_id=item.source_id,
                    rule_id=item.rule_id,
                    severity=item.severity,
                    title=item.title,
                    bureau=item.bureau,
                    tradeline_index=item.tradeline_index,
                    creditor_name=item.creditor_name,
                    account_number_masked=item.account_number_masked,
                    report_links=[
                        ComplianceEvidenceReportLink(
                            document_id=link.document_id,
                            bureau=link.bureau,
                            download_path=link.download_path,
                            page_numbers=list(link.page_numbers)
                            if link.page_numbers is not None
                            else None,
                            page_confidence=link.page_confidence,
                            excerpt_available=link.excerpt_available,
                        )
                        for link in item.report_links
                    ],
                    exhibit_links=[
                        ComplianceEvidenceExhibitLink(
                            document_id=link.document_id,
                            document_type=link.document_type,
                            role=link.role,
                            label=link.label,
                        )
                        for link in item.exhibit_links
                    ],
                    checklist_hints=list(item.checklist_hints),
                )
                for item in result.items
            ],
        )

    @staticmethod
    def _normalize_choice(value: str | None) -> str:
        if not value:
            return ""
        return value.strip().lower().replace("-", " ").replace("_", " ")

    @classmethod
    def _normalize_bureau(cls, value: object) -> str:
        bureau = cls._normalize_choice(cls._string_or_none(value))
        if bureau in {"equifax", "experian", "transunion", "innovis"}:
            return bureau
        if bureau == "trans union":
            return "transunion"
        return "unknown"

    @classmethod
    def _normalize_account_type(cls, value: object) -> str:
        account_type = cls._normalize_choice(cls._string_or_none(value))
        if "mortgage" in account_type:
            return "mortgage"
        if "auto" in account_type:
            return "auto"
        if "credit card" in account_type or "revolving" in account_type:
            return "credit_card"
        if "collection" in account_type:
            return "collection"
        if "student" in account_type:
            return "student_loan"
        if "medical" in account_type:
            return "medical"
        if "utility" in account_type:
            return "utility"
        if "telecom" in account_type or "wireless" in account_type:
            return "telecom"
        if "installment" in account_type or "personal" in account_type:
            return "personal_loan"
        return "other"

    @classmethod
    def _normalize_account_status(cls, value: object) -> str:
        account_status = cls._normalize_choice(cls._string_or_none(value))
        if not account_status:
            return "unknown"
        if "charge" in account_status and "off" in account_status:
            return "charge_off"
        if "repossession" in account_status:
            return "repossession"
        if "foreclosure" in account_status:
            return "foreclosure"
        if "transfer" in account_status:
            return "transferred"
        if "settled" in account_status:
            return "settled"
        if "deleted" in account_status:
            return "deleted"
        if "collection" in account_status:
            return "collection"
        if "paid" in account_status:
            return "paid"
        if "closed" in account_status:
            return "closed"
        if "current" in account_status or "open" in account_status or "late" in account_status:
            return "open"
        if "pays as agreed" in account_status:
            return "open"
        return "unknown"

    @classmethod
    def _normalize_payment_status(cls, value: object) -> str:
        payment_status = cls._normalize_choice(cls._string_or_none(value))
        if not payment_status:
            return "unknown"
        if "120" in payment_status:
            return "late_120"
        if "90" in payment_status:
            return "late_90"
        if "60" in payment_status:
            return "late_60"
        if "30" in payment_status:
            return "late_30"
        if "charge" in payment_status and "off" in payment_status:
            return "charge_off"
        if "collection" in payment_status:
            return "collection"
        if "repossession" in payment_status:
            return "repossession"
        if "foreclosure" in payment_status:
            return "foreclosure"
        if "current" in payment_status or "pays as agreed" in payment_status:
            return "current"
        return "unknown"

    @staticmethod
    def _money_string(value: object) -> str | None:
        normalized = DocumentService._float_or_none(value)
        if normalized is None:
            return None
        return f"{normalized:.2f}"

    @staticmethod
    def _parse_report_date(value: object) -> date | None:
        if not isinstance(value, str) or not value.strip():
            return None
        raw = value.strip()
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return None

    @classmethod
    def _candidate_from_account(
        cls,
        *,
        case_id: uuid.UUID,
        default_bureau: str,
        index: int,
        account: dict[str, Any],
    ) -> ParsedReportAccountCandidate | None:
        creditor_name = cls._string_or_none(account.get("creditor_name"))
        if not creditor_name:
            return None

        payment_status = cls._string_or_none(account.get("payment_status"))
        account_status = cls._string_or_none(account.get("account_status")) or payment_status
        remarks = (
            cls._string_or_none(account.get("remarks")) or "Imported from parsed credit report"
        )
        return ParsedReportAccountCandidate(
            source_index=index,
            case_id=case_id,
            bureau=cls._normalize_bureau(account.get("bureau") or default_bureau),
            creditor_name=creditor_name,
            original_creditor=cls._string_or_none(account.get("original_creditor")),
            account_number_masked=cls._string_or_none(account.get("account_number_masked")),
            account_type=cls._normalize_account_type(account.get("account_type")),
            account_status=cls._normalize_account_status(account_status),
            payment_status=cls._normalize_payment_status(payment_status),
            balance=cls._money_string(account.get("balance")),
            past_due_amount=cls._money_string(account.get("past_due_amount")),
            high_balance=cls._money_string(account.get("high_credit")),
            credit_limit=cls._money_string(account.get("credit_limit")),
            date_opened=cls._string_or_none(account.get("open_date")),
            date_reported=cls._string_or_none(account.get("date_reported")),
            date_first_delinquency=cls._string_or_none(account.get("date_first_delinquency")),
            remarks=remarks,
            payment_history=cls._string_or_none(account.get("payment_history")),
            date_closed=cls._string_or_none(account.get("date_closed")),
        )

    async def get_parsed_credit_report_account_candidates(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentParsedCreditReportAccountCandidatesResponse:
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

        accounts = parsed_report.parsed_report.get("accounts")
        candidates: list[ParsedReportAccountCandidate] = []
        if isinstance(accounts, list):
            for index, account in enumerate(accounts):
                if isinstance(account, dict):
                    candidate = self._candidate_from_account(
                        case_id=document.case_id,
                        default_bureau=parsed_report.bureau,
                        index=index,
                        account=account,
                    )
                    if candidate is not None:
                        candidates.append(candidate)

        return DocumentParsedCreditReportAccountCandidatesResponse(
            document_id=document.id,
            bureau=parsed_report.bureau,
            candidates=candidates,
        )

    async def import_parsed_credit_report_accounts(
        self,
        user: User,
        document_id: uuid.UUID,
        request: ImportParsedReportAccountsRequest,
    ) -> ImportParsedReportAccountsResponse:
        from decimal import Decimal

        from api.modules.accounts.models import (
            AccountBureau,
            AccountStatus,
            AccountType,
            PaymentStatus,
        )
        from api.modules.accounts.schemas import AccountCreate, AccountListParams
        from api.modules.accounts.service import AccountService
        from api.modules.documents.cross_bureau_comparison import tradeline_match_key

        self._require_write(user)
        document = await self._get_document_for_user(document_id, user)
        candidates_response = await self.get_parsed_credit_report_account_candidates(
            user,
            document_id,
        )
        if not candidates_response.candidates:
            return ImportParsedReportAccountsResponse(
                document_id=document_id,
                case_id=document.case_id,
                imported=[],
                skipped_indices=[],
            )

        case_id = candidates_response.candidates[0].case_id
        selected_indices = (
            set(request.source_indices)
            if request.source_indices is not None
            else {candidate.source_index for candidate in candidates_response.candidates}
        )

        account_service = AccountService.from_session(self._session)  # type: ignore[arg-type]
        existing_accounts = []
        page = 1
        while True:
            page_result = await account_service.list_case_accounts(
                user,
                case_id,
                params=AccountListParams(page=page, page_size=100),
            )
            existing_accounts.extend(page_result.items)
            if page >= page_result.pages:
                break
            page += 1

        existing_by_key = {
            tradeline_match_key(account.creditor_name, account.account_number_masked): account
            for account in existing_accounts
        }

        imported: list[ImportedParsedReportAccountItem] = []
        skipped_indices: list[int] = []

        for candidate in candidates_response.candidates:
            if candidate.source_index not in selected_indices:
                continue

            match_key = tradeline_match_key(
                candidate.creditor_name,
                candidate.account_number_masked,
            )
            if request.skip_existing and match_key in existing_by_key:
                skipped_indices.append(candidate.source_index)
                continue

            account = await account_service.create_account(
                user,
                AccountCreate(
                    case_id=case_id,
                    bureau=AccountBureau(candidate.bureau)
                    if candidate.bureau in {"experian", "equifax", "transunion", "innovis"}
                    else AccountBureau.UNKNOWN,
                    creditor_name=candidate.creditor_name,
                    original_creditor=candidate.original_creditor,
                    account_number_masked=candidate.account_number_masked,
                    account_type=AccountType(self._normalize_account_type(candidate.account_type)),
                    account_status=AccountStatus(
                        self._normalize_account_status(candidate.account_status)
                    ),
                    payment_status=PaymentStatus(
                        self._normalize_payment_status(candidate.payment_status)
                    ),
                    balance=Decimal(candidate.balance) if candidate.balance else None,
                    high_balance=(
                        Decimal(candidate.high_balance) if candidate.high_balance else None
                    ),
                    credit_limit=(
                        Decimal(candidate.credit_limit) if candidate.credit_limit else None
                    ),
                    past_due_amount=(
                        Decimal(candidate.past_due_amount) if candidate.past_due_amount else None
                    ),
                    date_opened=self._parse_report_date(candidate.date_opened),
                    date_reported=self._parse_report_date(candidate.date_reported),
                    date_first_delinquency=self._parse_report_date(
                        candidate.date_first_delinquency
                    ),
                    remarks=candidate.remarks,
                ),
            )
            imported.append(
                ImportedParsedReportAccountItem(
                    source_index=candidate.source_index,
                    account_id=account.id,
                    created=True,
                    creditor_name=candidate.creditor_name,
                )
            )
            existing_by_key[match_key] = account

        return ImportParsedReportAccountsResponse(
            document_id=document_id,
            case_id=case_id,
            imported=imported,
            skipped_indices=skipped_indices,
        )

    def _latest_parsed_reports_by_bureau(
        self,
        parsed_reports: list[DocumentParsedCreditReport],
    ) -> dict[str, tuple[uuid.UUID, dict[str, object]]]:
        latest: dict[str, tuple[uuid.UUID, dict[str, object]]] = {}
        for parsed_report in parsed_reports:
            bureau = str(parsed_report.bureau).lower()
            if bureau in latest:
                continue
            latest[bureau] = (parsed_report.document_id, parsed_report.parsed_report)
        return latest

    def _discrepancies_response(
        self,
        result: CrossBureauComparisonResult,
    ) -> CaseCreditReportDiscrepanciesResponse:
        return CaseCreditReportDiscrepanciesResponse(
            case_id=result.case_id,
            reports_compared=list(result.reports_compared),
            document_ids_by_bureau={
                bureau: document_id for bureau, document_id in result.document_ids_by_bureau.items()
            },
            summary=CrossBureauComparisonSummary(**result.summary),
            discrepancies=[
                CrossBureauDiscrepancyResponse(
                    match_key=item.match_key,
                    creditor_name=item.creditor_name,
                    account_number_masked=item.account_number_masked,
                    discrepancy_types=list(item.discrepancy_types),
                    classification=item.classification,
                    classification_label=item.classification_label,
                    confidence_score=item.confidence_score,
                    workflow_tier=item.workflow_tier,
                    bureaus_reporting=list(item.bureaus_reporting),
                    bureaus_missing=list(item.bureaus_missing),
                    bureau_snapshots=[
                        BureauTradelineSnapshotResponse(
                            bureau=snapshot.bureau,
                            document_id=snapshot.document_id,
                            creditor_name=snapshot.creditor_name,
                            account_number_masked=snapshot.account_number_masked,
                            balance=snapshot.balance,
                            past_due_amount=snapshot.past_due_amount,
                            payment_status=snapshot.payment_status,
                            account_status=snapshot.account_status,
                            account_type=snapshot.account_type,
                            high_credit=snapshot.high_credit,
                            credit_limit=snapshot.credit_limit,
                            open_date=snapshot.open_date,
                            date_closed=snapshot.date_closed,
                            date_first_delinquency=snapshot.date_first_delinquency,
                            date_reported=snapshot.date_reported,
                        )
                        for snapshot in item.bureau_snapshots
                    ],
                    field_diffs=[
                        ParsedReportFieldDiff(
                            field=diff.field,
                            previous=diff.previous,
                            current=diff.current,
                        )
                        for diff in item.field_diffs
                    ],
                    possible_causes=[
                        CrossBureauPossibleCauseResponse(
                            label=cause.label,
                            likelihood=cause.likelihood,
                        )
                        for cause in item.possible_causes
                    ],
                    recommended_next_step=item.recommended_next_step,
                    recommended_action=item.recommended_action,
                    requires_investigation=item.requires_investigation,
                    dispute_ready=item.dispute_ready,
                    is_actionable=item.is_actionable,
                )
                for item in result.discrepancies
            ],
        )

    async def get_case_credit_report_discrepancies(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseCreditReportDiscrepanciesResponse:
        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        parsed_reports = await self._documents.list_case_parsed_credit_reports(
            organization_id=organization_id,
            case_id=case_id,
        )
        reports_by_bureau = self._latest_parsed_reports_by_bureau(parsed_reports)
        if len(reports_by_bureau) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least two bureau credit reports are required for cross-bureau comparison",
            )

        result = compare_cross_bureau_reports(
            case_id=case_id,
            reports_by_bureau=reports_by_bureau,
        )
        return self._discrepancies_response(result)

    async def prepare_case_credit_report_disputes(
        self,
        user: User,
        case_id: uuid.UUID,
        request: PrepareCreditReportDisputesRequest,
    ) -> PrepareCreditReportDisputesResponse:
        from decimal import Decimal

        from api.modules.accounts.models import (
            AccountBureau,
            AccountStatus,
            AccountType,
            DisputeStatus,
            PaymentStatus,
        )
        from api.modules.accounts.schemas import AccountCreate, AccountListParams
        from api.modules.accounts.service import AccountService
        from api.modules.documents.cross_bureau_comparison import tradeline_match_key

        self._require_write(user)
        discrepancies = await self.get_case_credit_report_discrepancies(user, case_id)
        selected_keys = set(request.match_keys) if request.match_keys else None

        account_service = AccountService.from_session(self._session)  # type: ignore[arg-type]
        existing_accounts = []
        page = 1
        while True:
            page_result = await account_service.list_case_accounts(
                user,
                case_id,
                params=AccountListParams(page=page, page_size=100),
            )
            existing_accounts.extend(page_result.items)
            if page >= page_result.pages:
                break
            page += 1
        existing_by_key = {
            tradeline_match_key(account.creditor_name, account.account_number_masked): account
            for account in existing_accounts
        }

        prepared: list[PreparedCreditReportDisputeItem] = []
        skipped: list[str] = []

        for discrepancy in discrepancies.discrepancies:
            if not discrepancy.dispute_ready:
                skipped.append(discrepancy.match_key)
                continue
            if selected_keys is not None and discrepancy.match_key not in selected_keys:
                continue

            existing = existing_by_key.get(discrepancy.match_key)
            created_account = False
            if existing is None:
                primary = max(
                    discrepancy.bureau_snapshots,
                    key=lambda snapshot: snapshot.balance or 0.0,
                )
                account = await account_service.create_account(
                    user,
                    AccountCreate(
                        case_id=case_id,
                        bureau=AccountBureau(primary.bureau)
                        if primary.bureau in {"experian", "equifax", "transunion"}
                        else AccountBureau.UNKNOWN,
                        creditor_name=discrepancy.creditor_name,
                        account_number_masked=discrepancy.account_number_masked,
                        account_type=AccountType(
                            self._normalize_account_type(primary.account_type)
                        ),
                        account_status=AccountStatus(
                            self._normalize_account_status(primary.payment_status)
                        ),
                        payment_status=PaymentStatus(
                            self._normalize_payment_status(primary.payment_status)
                        ),
                        balance=Decimal(str(primary.balance))
                        if primary.balance is not None
                        else None,
                        remarks=(
                            "Cross-bureau discrepancy detected: "
                            f"{', '.join(discrepancy.discrepancy_types)}. "
                            f"{discrepancy.recommended_action}"
                        ),
                        dispute_status=DisputeStatus.READY_FOR_DISPUTE,
                    ),
                )
                account_id = account.id
                created_account = True
                existing_by_key[discrepancy.match_key] = account
            else:
                account_id = existing.id

            dispute_letter = await account_service.create_dispute_letter_draft(
                user,
                account_id,
                recipient_type=request.recipient_type,
            )
            prepared.append(
                PreparedCreditReportDisputeItem(
                    match_key=discrepancy.match_key,
                    account_id=account_id,
                    dispute_letter_id=dispute_letter.id,
                    created_account=created_account,
                    creditor_name=discrepancy.creditor_name,
                    recommended_action=discrepancy.recommended_action,
                )
            )

        return PrepareCreditReportDisputesResponse(
            case_id=case_id,
            prepared=prepared,
            skipped=skipped,
        )

    async def create_parsed_credit_report_review_task(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> TaskResponse:
        self._require_write(user)
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

        candidates = (
            await self.get_parsed_credit_report_account_candidates(user, document_id)
        ).candidates
        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Parsed credit report has no account candidates to review",
            )

        if self._tasks is not None:
            existing = await self._tasks.find_active_by_source(
                organization_id=document.organization_id,
                document_id=document.id,
                source_module=PARSED_REPORT_REVIEW_TASK_SOURCE,
                source_event_id=parsed_report.id,
            )
            if existing is not None:
                return TaskResponse.from_model(existing)

        task = Task(
            organization_id=document.organization_id,
            case_id=document.case_id,
            document_id=document.id,
            title=f"Review {len(candidates)} account candidate(s) from {document.title}",
            description=(
                "Review parsed credit report tradelines and create account records "
                "for candidate tradelines that should be tracked."
            ),
            priority=TaskPriority.HIGH,
            due_date=datetime.now(UTC) + timedelta(days=1),
            source_module=PARSED_REPORT_REVIEW_TASK_SOURCE,
            source_event_id=parsed_report.id,
        )
        apply_audit_on_create(task, user.id)
        if self._tasks is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task repository is not configured",
            )
        await self._tasks.create(task)
        if self._session is not None:
            await publish_platform_event(self._session, task_created_event(task, user.id))
        return TaskResponse.from_model(task)

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
