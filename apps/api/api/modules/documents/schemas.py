"""Documents domain schemas."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field
from sqlalchemy import inspect as sa_inspect

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.documents.constants import (
    ClassificationMethod,
    DocumentProcessingStatus,
    DocumentType,
    MetadataStatus,
    ResolutionStatus,
)
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport

if TYPE_CHECKING:
    from api.modules.documents.strategy_run_models import DisputeStrategyRun

DocumentSortField = Literal["created_at", "title", "file_name", "file_size"]
DocumentSortOrder = Literal["asc", "desc"]


class DocumentUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    account_id: uuid.UUID | None = None


class DocumentListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    is_duplicate: bool | None = None
    processing_status: DocumentProcessingStatus | None = None
    metadata_status: MetadataStatus | None = None
    resolution_status: ResolutionStatus | None = None
    sort_by: DocumentSortField = "created_at"
    sort_order: DocumentSortOrder = "desc"


class DocumentVersionResponse(BaseSchema):
    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    file_name: str
    mime_type: str | None
    file_size: int | None
    file_hash: str
    created_at: datetime
    created_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, version: DocumentVersion) -> "DocumentVersionResponse":
        return cls(
            id=version.id,
            document_id=version.document_id,
            version_number=version.version_number,
            file_name=version.file_name,
            mime_type=version.mime_type,
            file_size=version.file_size,
            file_hash=version.file_hash,
            created_at=version.created_at,
            created_by_id=version.created_by_id,
        )


class DocumentResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID
    account_id: uuid.UUID | None
    title: str
    description: str | None
    file_name: str
    mime_type: str | None
    file_size: int | None
    file_hash: str
    version_number: int
    is_duplicate: bool
    duplicate_of_id: uuid.UUID | None
    processing_status: DocumentProcessingStatus
    ocr_processed_at: datetime | None
    ocr_version_number: int | None
    document_type: DocumentType | None = None
    confidence_score: float | None = None
    classified_at: datetime | None = None
    metadata_status: MetadataStatus | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None
    versions: list[DocumentVersionResponse] = Field(default_factory=list)

    @classmethod
    def from_model(
        cls,
        document: Document,
        *,
        include_versions: bool = False,
    ) -> "DocumentResponse":
        versions: list[DocumentVersionResponse] = []
        if include_versions and document.versions:
            versions = [DocumentVersionResponse.from_model(v) for v in document.versions]
        unloaded = sa_inspect(document).unloaded
        extracted_metadata = (
            document.extracted_metadata if "extracted_metadata" not in unloaded else None
        )
        return cls(
            id=document.id,
            organization_id=document.organization_id,
            case_id=document.case_id,
            account_id=document.account_id,
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            mime_type=document.mime_type,
            file_size=document.file_size,
            file_hash=document.file_hash,
            version_number=document.version_number,
            is_duplicate=document.is_duplicate,
            duplicate_of_id=document.duplicate_of_id,
            processing_status=DocumentProcessingStatus(document.processing_status),
            ocr_processed_at=document.ocr_processed_at,
            ocr_version_number=document.ocr_version_number,
            document_type=(
                DocumentType(document.document_type) if document.document_type else None
            ),
            confidence_score=float(document.confidence_score)
            if document.confidence_score is not None
            else None,
            classified_at=document.classified_at,
            metadata_status=(
                MetadataStatus(extracted_metadata.metadata_status)
                if extracted_metadata is not None
                else None
            ),
            created_at=document.created_at,
            updated_at=document.updated_at,
            deleted_at=document.deleted_at,
            created_by_id=document.created_by_id,
            updated_by_id=document.updated_by_id,
            versions=versions,
        )


class DocumentDuplicateGroupResponse(BaseSchema):
    document_id: uuid.UUID
    canonical_document: DocumentResponse
    duplicate_documents: list[DocumentResponse]
    duplicate_count: int

    @classmethod
    def from_group(
        cls,
        *,
        document_id: uuid.UUID,
        canonical_document: Document,
        duplicate_documents: list[Document],
    ) -> "DocumentDuplicateGroupResponse":
        return cls(
            document_id=document_id,
            canonical_document=DocumentResponse.from_model(canonical_document),
            duplicate_documents=[
                DocumentResponse.from_model(document) for document in duplicate_documents
            ],
            duplicate_count=len(duplicate_documents),
        )


class DocumentOcrResponse(BaseSchema):
    document_id: uuid.UUID
    processing_status: DocumentProcessingStatus
    ocr_text: str | None
    ocr_error: str | None
    ocr_processed_at: datetime | None
    ocr_version_number: int | None

    @classmethod
    def from_model(cls, document: Document) -> "DocumentOcrResponse":
        return cls(
            document_id=document.id,
            processing_status=DocumentProcessingStatus(document.processing_status),
            ocr_text=document.ocr_text,
            ocr_error=document.ocr_error,
            ocr_processed_at=document.ocr_processed_at,
            ocr_version_number=document.ocr_version_number,
        )


class DocumentCreditReportReparseResponse(BaseSchema):
    document_id: uuid.UUID
    job_id: str
    job_type: str
    queued: bool = True


class DocumentMetadataReextractResponse(BaseSchema):
    document_id: uuid.UUID
    job_id: str
    job_type: str
    queued: bool = True


class CaseCreditReportReparseQueuedItem(BaseSchema):
    document_id: uuid.UUID
    job_id: str
    job_type: str


class CaseCreditReportReparseSkippedItem(BaseSchema):
    document_id: uuid.UUID
    reason: str


class CaseCreditReportBulkReparseResponse(BaseSchema):
    case_id: uuid.UUID
    queued_count: int
    skipped_count: int
    queued: list[CaseCreditReportReparseQueuedItem]
    skipped: list[CaseCreditReportReparseSkippedItem]


class CaseMetadataReextractQueuedItem(BaseSchema):
    document_id: uuid.UUID
    job_id: str
    job_type: str


class CaseMetadataReextractSkippedItem(BaseSchema):
    document_id: uuid.UUID
    reason: str


class CaseMetadataBulkReextractResponse(BaseSchema):
    case_id: uuid.UUID
    queued_count: int
    skipped_count: int
    queued: list[CaseMetadataReextractQueuedItem]
    skipped: list[CaseMetadataReextractSkippedItem]


class DocumentLlmSummaryResponse(BaseSchema):
    document_id: uuid.UUID
    summary: str
    model: str
    provider: str
    prompt_hash: str
    generated_at: datetime
    pii_scrubbed: bool = True


class DocumentClassificationResponse(BaseSchema):
    document_id: uuid.UUID
    document_type: DocumentType | None
    confidence_score: float | None
    classification_method: ClassificationMethod | None
    classified_at: datetime | None
    classified_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, document: Document) -> "DocumentClassificationResponse":
        return cls(
            document_id=document.id,
            document_type=(
                DocumentType(document.document_type) if document.document_type else None
            ),
            confidence_score=float(document.confidence_score)
            if document.confidence_score is not None
            else None,
            classification_method=(
                ClassificationMethod(document.classification_method)
                if document.classification_method
                else None
            ),
            classified_at=document.classified_at,
            classified_by_id=document.classified_by_id,
        )


class DocumentParsedCreditReportResponse(BaseSchema):
    document_id: uuid.UUID
    schema_version: str
    bureau: str
    parser_name: str
    parser_confidence: float
    parsed_report: dict[str, Any]
    is_partial: bool
    warnings: list[str]
    parsed_at: datetime

    @classmethod
    def from_model(
        cls,
        parsed_report: DocumentParsedCreditReport,
    ) -> "DocumentParsedCreditReportResponse":
        return cls(
            document_id=parsed_report.document_id,
            schema_version=parsed_report.schema_version,
            bureau=parsed_report.bureau,
            parser_name=parsed_report.parser_name,
            parser_confidence=float(parsed_report.parser_confidence),
            parsed_report=parsed_report.parsed_report,
            is_partial=parsed_report.is_partial,
            warnings=list(parsed_report.warnings or []),
            parsed_at=parsed_report.parsed_at,
        )


class ParsedReportFieldDiff(BaseSchema):
    field: str
    previous: str | float | None = None
    current: str | float | None = None


class ParsedReportAccountChange(BaseSchema):
    match_key: str
    creditor_name: str | None
    account_number_masked: str | None
    change_type: Literal["added", "removed", "changed", "unchanged"]
    previous_balance: float | None = None
    current_balance: float | None = None
    balance_delta: float | None = None
    previous_payment_status: str | None = None
    current_payment_status: str | None = None
    field_diffs: list[ParsedReportFieldDiff] = []


class ParsedReportComparisonSummary(BaseSchema):
    added: int
    removed: int
    changed: int
    unchanged: int


class DocumentParsedCreditReportComparisonResponse(BaseSchema):
    document_id: uuid.UUID
    bureau: str
    previous_document_id: uuid.UUID | None
    current_parsed_at: datetime
    previous_parsed_at: datetime | None
    summary: ParsedReportComparisonSummary
    account_changes: list[ParsedReportAccountChange]


class ParsedReportAccountCandidate(BaseSchema):
    source_index: int
    case_id: uuid.UUID
    bureau: str
    creditor_name: str
    original_creditor: str | None = None
    account_number_masked: str | None = None
    account_type: str
    account_status: str
    payment_status: str
    balance: str | None = None
    past_due_amount: str | None = None
    high_balance: str | None = None
    credit_limit: str | None = None
    date_opened: str | None = None
    date_reported: str | None = None
    date_first_delinquency: str | None = None
    remarks: str | None = None
    payment_history: str | None = None
    date_closed: str | None = None


class DocumentParsedCreditReportAccountCandidatesResponse(BaseSchema):
    document_id: uuid.UUID
    bureau: str
    candidates: list[ParsedReportAccountCandidate]


class ImportParsedReportAccountsRequest(BaseSchema):
    source_indices: list[int] | None = None
    skip_existing: bool = True


class ImportedParsedReportAccountItem(BaseSchema):
    source_index: int
    account_id: uuid.UUID
    created: bool
    creditor_name: str


class ImportParsedReportAccountsResponse(BaseSchema):
    document_id: uuid.UUID
    case_id: uuid.UUID
    imported: list[ImportedParsedReportAccountItem]
    skipped_indices: list[int]


class BureauTradelineSnapshotResponse(BaseSchema):
    bureau: str
    document_id: uuid.UUID
    creditor_name: str
    account_number_masked: str | None = None
    balance: float | None = None
    past_due_amount: float | None = None
    payment_status: str | None = None
    account_status: str | None = None
    account_type: str | None = None
    high_credit: float | None = None
    credit_limit: float | None = None
    open_date: str | None = None
    date_closed: str | None = None
    date_first_delinquency: str | None = None
    date_reported: str | None = None


class CrossBureauPossibleCauseResponse(BaseSchema):
    label: str
    likelihood: Literal["most_likely", "possible", "less_likely"]


class CrossBureauDiscrepancyResponse(BaseSchema):
    match_key: str
    creditor_name: str
    account_number_masked: str | None = None
    discrepancy_types: list[str]
    classification: str
    classification_label: str
    confidence_score: int
    workflow_tier: Literal["none", "investigation", "dispute"]
    bureaus_reporting: list[str]
    bureaus_missing: list[str]
    bureau_snapshots: list[BureauTradelineSnapshotResponse]
    field_diffs: list[ParsedReportFieldDiff] = []
    possible_causes: list[CrossBureauPossibleCauseResponse]
    recommended_next_step: str
    recommended_action: str
    requires_investigation: bool
    dispute_ready: bool
    is_actionable: bool


class CrossBureauComparisonSummary(BaseSchema):
    total_tradelines: int
    actionable: int
    investigation_needed: int
    dispute_ready: int
    consistent: int
    missing_from_bureau: int
    balance_mismatch: int
    status_mismatch: int
    past_due_mismatch: int = 0
    dofd_mismatch: int = 0


class CaseCreditReportDiscrepanciesResponse(BaseSchema):
    case_id: uuid.UUID
    reports_compared: list[str]
    document_ids_by_bureau: dict[str, uuid.UUID]
    summary: CrossBureauComparisonSummary
    discrepancies: list[CrossBureauDiscrepancyResponse]


class PrepareCreditReportDisputesRequest(BaseSchema):
    match_keys: list[str] | None = None
    recipient_type: Literal["credit_bureau", "furnisher"] = "credit_bureau"


class PreparedCreditReportDisputeItem(BaseSchema):
    match_key: str
    account_id: uuid.UUID
    dispute_letter_id: uuid.UUID | None = None
    created_account: bool
    creditor_name: str
    recommended_action: str


class LockedDisputePreparationItem(BaseSchema):
    """A tradeline skipped during bulk preparation because of an identity-theft lock."""

    match_key: str
    creditor_name: str | None = None
    reason: str


class PrepareCreditReportDisputesResponse(BaseSchema):
    case_id: uuid.UUID
    prepared: list[PreparedCreditReportDisputeItem]
    skipped: list[str]
    locked: list[LockedDisputePreparationItem] = []


class Metro2FindingSummary(BaseSchema):
    total: int
    high: int
    medium: int
    low: int
    tradelines_evaluated: int


class Metro2FindingResponse(BaseSchema):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    title: str
    description: str
    tradeline_index: int
    creditor_name: str | None = None
    account_number_masked: str | None = None
    fields: list[str]
    observed: dict[str, object]


class DocumentMetro2FindingsResponse(BaseSchema):
    document_id: uuid.UUID
    bureau: str
    schema_version: str | None = None
    summary: Metro2FindingSummary
    findings: list[Metro2FindingResponse]


class CaseMetro2FindingsResponse(BaseSchema):
    case_id: uuid.UUID
    reports_evaluated: list[str]
    document_ids_by_bureau: dict[str, uuid.UUID]
    summary: Metro2FindingSummary
    documents: list[DocumentMetro2FindingsResponse]


class FcraFindingSummary(BaseSchema):
    total: int
    high: int
    medium: int
    low: int
    tradelines_evaluated: int


class FcraFindingResponse(BaseSchema):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    title: str
    description: str
    fcra_sections: list[str]
    tradeline_index: int
    creditor_name: str | None = None
    account_number_masked: str | None = None
    fields: list[str]
    observed: dict[str, object]


class DocumentFcraFindingsResponse(BaseSchema):
    document_id: uuid.UUID
    bureau: str
    schema_version: str | None = None
    as_of_date: str | None = None
    summary: FcraFindingSummary
    findings: list[FcraFindingResponse]


class CaseFcraFindingsResponse(BaseSchema):
    case_id: uuid.UUID
    reports_evaluated: list[str]
    document_ids_by_bureau: dict[str, uuid.UUID]
    summary: FcraFindingSummary
    documents: list[DocumentFcraFindingsResponse]


class TradelineChronologySummary(BaseSchema):
    tradelines: int
    with_changes: int
    snapshots: int
    events: int
    reports_evaluated: int


class TradelineChronologySnapshotResponse(BaseSchema):
    document_id: uuid.UUID
    parsed_at: datetime
    as_of_date: str | None = None
    present: bool
    creditor_name: str | None = None
    account_number_masked: str | None = None
    balance: float | None = None
    past_due_amount: float | None = None
    account_status: str | None = None
    payment_status: str | None = None
    date_first_delinquency: str | None = None
    date_closed: str | None = None
    remarks: str | None = None
    high_credit: float | None = None
    credit_limit: float | None = None


class TradelineChronologyEventResponse(BaseSchema):
    event_type: Literal[
        "appeared",
        "disappeared",
        "balance_increased",
        "balance_decreased",
        "past_due_changed",
        "status_changed",
        "dofd_changed",
        "date_closed_changed",
        "field_changed",
    ]
    severity: Literal["low", "medium", "high"]
    field: str | None = None
    from_document_id: uuid.UUID | None = None
    to_document_id: uuid.UUID
    from_parsed_at: datetime | None = None
    to_parsed_at: datetime
    previous: str | float | None = None
    current: str | float | None = None
    summary: str


class TradelineChronologyItemResponse(BaseSchema):
    match_key: str
    bureau: str
    creditor_name: str | None = None
    account_number_masked: str | None = None
    snapshot_count: int
    event_count: int
    snapshots: list[TradelineChronologySnapshotResponse]
    events: list[TradelineChronologyEventResponse]


class CaseTradelineChronologyResponse(BaseSchema):
    case_id: uuid.UUID
    reports_evaluated: int
    bureaus: list[str]
    summary: TradelineChronologySummary
    tradelines: list[TradelineChronologyItemResponse]


class ComplianceEvidenceSummary(BaseSchema):
    findings_linked: int
    with_pages: int
    missing_pages: int
    exhibits_available: int
    report_links: int


class ComplianceEvidenceReportLink(BaseSchema):
    document_id: uuid.UUID
    bureau: str | None = None
    download_path: str
    page_numbers: list[int] | None = None
    page_confidence: Literal["matched", "unavailable", "deferred"]
    excerpt_available: bool


class ComplianceEvidenceExhibitLink(BaseSchema):
    document_id: uuid.UUID
    document_type: str
    role: Literal["identity", "proof_of_address", "supporting", "suggested"]
    label: str


class ComplianceEvidenceLinkItem(BaseSchema):
    source_kind: Literal["metro2", "fcra"]
    source_id: str
    rule_id: str
    severity: str
    title: str
    bureau: str | None = None
    tradeline_index: int | None = None
    creditor_name: str | None = None
    account_number_masked: str | None = None
    report_links: list[ComplianceEvidenceReportLink]
    exhibit_links: list[ComplianceEvidenceExhibitLink]
    checklist_hints: list[str]


class CaseComplianceEvidenceLinksResponse(BaseSchema):
    case_id: uuid.UUID
    summary: ComplianceEvidenceSummary
    items: list[ComplianceEvidenceLinkItem]


class LitigationStrengthSummary(BaseSchema):
    issues_scored: int
    high_priority: int
    medium_priority: int
    low_priority: int
    top_score: int
    average_score: float


class LitigationStrengthIssue(BaseSchema):
    source_kind: Literal["metro2", "fcra", "cross_bureau", "chronology", "identity_theft"]
    source_id: str
    rule_id: str
    score: int
    rank: int
    title: str
    rationale: str
    severity: str
    bureau: str | None = None
    creditor_name: str | None = None
    account_number_masked: str | None = None
    match_key: str | None = None
    factors: list[str]


class CaseLitigationStrengthResponse(BaseSchema):
    case_id: uuid.UUID
    summary: LitigationStrengthSummary
    issues: list[LitigationStrengthIssue]


class DisputeStrategySummary(BaseSchema):
    accounts_planned: int
    issues_covered: int
    high_strength_accounts: int
    cfpb_recommended: int
    attorney_recommended: int


class DisputeStrategyStage(BaseSchema):
    stage_order: int
    stage_kind: Literal[
        "cra_dispute",
        "furnisher_dispute",
        "cfpb_escalation",
        "attorney_preserve",
    ]
    title: str
    objective: str
    rationale: str
    issue_source_ids: list[str]
    evidence_hints: list[str]
    recommended: bool


class AccountDisputeStrategyItem(BaseSchema):
    account_key: str
    creditor_name: str | None = None
    account_number_masked: str | None = None
    bureau: str | None = None
    match_key: str | None = None
    top_score: int
    issue_count: int
    primary_rule_ids: list[str]
    summary: str
    stages: list[DisputeStrategyStage]


class CaseDisputeStrategyResponse(BaseSchema):
    case_id: uuid.UUID
    disclaimer: str
    summary: DisputeStrategySummary
    strategies: list[AccountDisputeStrategyItem]
    run_id: uuid.UUID | None = None
    generated_at: datetime | None = None


class DisputeStrategyRunSummaryResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    generated_at: datetime
    generated_by_id: uuid.UUID | None = None
    accounts_planned: int
    issues_covered: int
    high_strength_accounts: int
    cfpb_recommended: int
    attorney_recommended: int

    @classmethod
    def from_model(cls, run: "DisputeStrategyRun") -> "DisputeStrategyRunSummaryResponse":
        summary = run.payload.get("summary", {})
        return cls(
            id=run.id,
            case_id=run.case_id,
            generated_at=run.generated_at,
            generated_by_id=run.generated_by_id,
            accounts_planned=run.accounts_planned,
            issues_covered=run.issues_covered,
            high_strength_accounts=int(summary.get("high_strength_accounts", 0)),
            cfpb_recommended=int(summary.get("cfpb_recommended", 0)),
            attorney_recommended=int(summary.get("attorney_recommended", 0)),
        )


class DisputeStrategyRunListParams(PaginationParams):
    pass


class DisputeStrategyRunResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    generated_at: datetime
    generated_by_id: uuid.UUID | None = None
    disclaimer: str
    summary: DisputeStrategySummary
    strategies: list[AccountDisputeStrategyItem]
    accounts_planned: int
    issues_covered: int

    @classmethod
    def from_model(cls, run: "DisputeStrategyRun") -> "DisputeStrategyRunResponse":
        payload = run.payload
        return cls(
            id=run.id,
            case_id=run.case_id,
            generated_at=run.generated_at,
            generated_by_id=run.generated_by_id,
            disclaimer=str(payload["disclaimer"]),
            summary=DisputeStrategySummary(**payload["summary"]),
            strategies=[AccountDisputeStrategyItem(**item) for item in payload["strategies"]],
            accounts_planned=run.accounts_planned,
            issues_covered=run.issues_covered,
        )


class PrepareDisputeStrategyStageRequest(BaseSchema):
    stage_kind: Literal["cra_dispute", "furnisher_dispute"]
    account_keys: list[str] | None = None
    recommended_only: bool = True


class PrepareDisputeStrategyStageResponse(BaseSchema):
    case_id: uuid.UUID
    stage_kind: Literal["cra_dispute", "furnisher_dispute"]
    recipient_type: Literal["credit_bureau", "furnisher"]
    match_keys: list[str]
    direct_account_keys: list[str] = []
    prepared: list[PreparedCreditReportDisputeItem]
    skipped: list[str]
    locked: list[LockedDisputePreparationItem] = []
    note: str | None = None


class CfpbChecklistSummary(BaseSchema):
    accounts_listed: int
    required_items: int
    optional_items: int
    items_present: int = 0
    items_missing: int = 0
    items_unknown: int = 0


class CfpbChecklistItem(BaseSchema):
    item_id: str
    category: Literal["correspondence", "evidence", "chronology", "filing"]
    title: str
    detail: str
    required: bool
    completion_status: Literal["present", "missing", "unknown"] = "unknown"
    completion_source: Literal["computed", "staff"] = "computed"
    override_note: str | None = None


class AccountCfpbChecklistItem(BaseSchema):
    account_key: str
    creditor_name: str | None = None
    account_number_masked: str | None = None
    bureau: str | None = None
    match_key: str | None = None
    top_score: int
    primary_rule_ids: list[str]
    items: list[CfpbChecklistItem]


class CaseCfpbChecklistResponse(BaseSchema):
    case_id: uuid.UUID
    disclaimer: str
    summary: CfpbChecklistSummary
    accounts: list[AccountCfpbChecklistItem]


class AttorneyChecklistSummary(BaseSchema):
    accounts_listed: int
    required_items: int
    optional_items: int
    escalation_flagged: int
    items_present: int = 0
    items_missing: int = 0
    items_unknown: int = 0


class AttorneyChecklistItem(BaseSchema):
    item_id: str
    category: Literal["correspondence", "evidence", "chronology", "filing"]
    title: str
    detail: str
    required: bool
    completion_status: Literal["present", "missing", "unknown"] = "unknown"
    completion_source: Literal["computed", "staff"] = "computed"
    override_note: str | None = None


class AccountAttorneyChecklistItem(BaseSchema):
    account_key: str
    creditor_name: str | None = None
    account_number_masked: str | None = None
    bureau: str | None = None
    match_key: str | None = None
    top_score: int
    primary_rule_ids: list[str]
    attorney_escalation: bool
    items: list[AttorneyChecklistItem]


class CaseAttorneyChecklistResponse(BaseSchema):
    case_id: uuid.UUID
    disclaimer: str
    summary: AttorneyChecklistSummary
    accounts: list[AccountAttorneyChecklistItem]


class UpsertChecklistOverrideRequest(BaseSchema):
    checklist_kind: Literal["cfpb", "attorney"]
    account_key: str
    item_id: str
    completion_status: Literal["present", "missing", "unknown"] | None = None
    note: str | None = None


# --- Identity Theft Detection & Recovery (Phase 8) ---

IdentityTheftConfirmationChoice = Literal[
    "recognize",
    "need_more_info",
    "inaccurate_reporting",
    "identity_theft",
    "mixed_file",
    "authorized_user",
    "unsure",
]


class IdentityTheftFindingSummary(BaseSchema):
    total: int
    high: int
    medium: int
    low: int
    tradelines_evaluated: int
    report_level_indicators: int = 0
    tradeline_indicators: int = 0
    personal_info_indicators: int = 0
    ordinary_dispute_locked_count: int = 0


class IdentityTheftFindingResponse(BaseSchema):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    title: str
    description: str
    detection_source: Literal[
        "REPORT_TEXT", "TRADELINE_HEURISTIC", "CONSUMER_CONFIRMATION", "PERSONAL_INFO"
    ]
    issue_type: Literal["IDENTITY_THEFT_INDICATOR", "CONFIRMED_IDENTITY_THEFT_CLAIM"]
    confidence: float
    consumer_confirmed: bool
    legal_path: Literal["FCRA_605B"] | None = None
    ordinary_dispute_locked: bool
    required_action: Literal[
        "CONSUMER_REVIEW",
        "OPEN_IDENTITY_THEFT_CASE",
        "PREPARE_605B",
        "CONTINUE_ORDINARY_DISPUTE",
    ]
    classification: dict[str, object]
    tradeline_index: int | None = None
    creditor_name: str | None = None
    account_number_masked: str | None = None
    fields: list[str]
    observed: dict[str, object]


class DocumentIdentityTheftFindingsResponse(BaseSchema):
    document_id: uuid.UUID
    bureau: str
    schema_version: str | None = None
    as_of_date: str | None = None
    banner_active: bool
    banner_title: str | None = None
    banner_body: str | None = None
    ordinary_dispute_locked: bool
    summary: IdentityTheftFindingSummary
    findings: list[IdentityTheftFindingResponse]
    protections_detected: list[dict[str, object]]


class CaseIdentityTheftFindingsResponse(BaseSchema):
    case_id: uuid.UUID
    reports_evaluated: list[str]
    document_ids_by_bureau: dict[str, uuid.UUID]
    banner_active: bool
    banner_title: str | None = None
    banner_body: str | None = None
    ordinary_dispute_locked: bool
    summary: IdentityTheftFindingSummary
    documents: list[DocumentIdentityTheftFindingsResponse]


class Fcra605bItemResponse(BaseSchema):
    item_id: str
    label: str
    required: bool
    status: Literal["present", "missing", "unknown"]


class Fcra605bReadinessResponse(BaseSchema):
    remedy_type: str
    not_ordinary_dispute: bool
    packet_readiness: int
    items: list[Fcra605bItemResponse]
    missing_evidence: list[str]


class Fcra605bReadinessRunResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    generated_at: datetime
    generated_by_id: uuid.UUID | None = None
    is_ready: bool
    packet_readiness: int | None = None
    confirmed_count: int
    attestation_recorded: bool
    bureaus: list[str] = []
    missing_evidence: list[str] = []
    blocking_reasons: list[str] = []


class Fcra605bReadinessRunListResponse(BaseSchema):
    items: list[Fcra605bReadinessRunResponse]
    total: int
    skip: int
    limit: int


class IdentityTheftIncidentResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    status: Literal["open", "in_recovery", "closed"]
    discovered_at: date | None = None
    suspected_theft_period_start: date | None = None
    suspected_theft_period_end: date | None = None
    unrecognized_addresses: list[object] = Field(default_factory=list)
    unrecognized_aliases: list[object] = Field(default_factory=list)
    companies_contacted: list[object] = Field(default_factory=list)
    police_report_number: str | None = None
    police_report_agency: str | None = None
    police_report_filed_at: date | None = None
    ftc_report_status: str
    ftc_report_reference: str | None = None
    evidence_checklist: list[object] = Field(default_factory=list)
    recovery_step: int
    consumer_attestation_at: datetime | None = None
    consumer_attestation_text: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class IdentityTheftAccountReviewResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    incident_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    bureau: str | None = None
    tradeline_index: int | None = None
    match_key: str | None = None
    creditor_name: str | None = None
    account_number_masked: str | None = None
    detection_source: str
    rule_id: str | None = None
    confidence: float
    issue_type: Literal["IDENTITY_THEFT_INDICATOR", "CONFIRMED_IDENTITY_THEFT_CLAIM"]
    consumer_confirmation: IdentityTheftConfirmationChoice | None = None
    consumer_confirmed_at: datetime | None = None
    ordinary_dispute_locked: bool
    legal_path: str | None = None
    packet_readiness: int | None = None
    missing_evidence: list[object] = Field(default_factory=list)
    attestation_accepted: bool
    classification: dict[str, object]
    created_at: datetime
    updated_at: datetime


class IdentityTheftProtectionResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    protection_type: Literal[
        "initial_fraud_alert",
        "extended_fraud_alert",
        "active_duty_alert",
        "equifax_freeze",
        "experian_freeze",
        "transunion_freeze",
    ]
    status: Literal["active", "inactive", "frozen", "unfrozen", "unknown"]
    placed_at: date | None = None
    expires_at: date | None = None
    source: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class IdentityTheftCaseCenterResponse(BaseSchema):
    case_id: uuid.UUID
    disclaimer: str
    confirmation_options: list[str]
    attestation_text: str
    recovery_workflow_steps: list[dict[str, str]]
    default_evidence_checklist: list[dict[str, str]]
    banner_active: bool
    banner_title: str | None = None
    banner_body: str | None = None
    findings: CaseIdentityTheftFindingsResponse | None = None
    incident: IdentityTheftIncidentResponse | None = None
    account_reviews: list[IdentityTheftAccountReviewResponse]
    protections: list[IdentityTheftProtectionResponse]
    fcra_605b: Fcra605bReadinessResponse | None = None


class ConfirmIdentityTheftAccountRequest(BaseSchema):
    confirmation: IdentityTheftConfirmationChoice
    attestation_accepted: bool = False
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    bureau: str | None = None
    tradeline_index: int | None = None
    match_key: str | None = None
    creditor_name: str | None = None
    account_number_masked: str | None = None
    detection_source: Literal[
        "REPORT_TEXT", "TRADELINE_HEURISTIC", "CONSUMER_CONFIRMATION", "PERSONAL_INFO"
    ] = "CONSUMER_CONFIRMATION"
    rule_id: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    discovered_at: date | None = None


class UpsertIdentityTheftProtectionRequest(BaseSchema):
    protection_type: Literal[
        "initial_fraud_alert",
        "extended_fraud_alert",
        "active_duty_alert",
        "equifax_freeze",
        "experian_freeze",
        "transunion_freeze",
    ]
    status: Literal["active", "inactive", "frozen", "unfrozen", "unknown"]
    placed_at: date | None = None
    expires_at: date | None = None
    notes: str | None = None


class UpdateIdentityTheftIncidentRequest(BaseSchema):
    status: Literal["open", "in_recovery", "closed"] | None = None
    discovered_at: date | None = None
    suspected_theft_period_start: date | None = None
    suspected_theft_period_end: date | None = None
    unrecognized_addresses: list[object] | None = None
    unrecognized_aliases: list[object] | None = None
    companies_contacted: list[object] | None = None
    police_report_number: str | None = None
    police_report_agency: str | None = None
    police_report_filed_at: date | None = None
    ftc_report_status: str | None = None
    ftc_report_reference: str | None = None
    evidence_checklist: list[object] | None = None
    recovery_step: int | None = Field(default=None, ge=1, le=9)
    notes: str | None = None
