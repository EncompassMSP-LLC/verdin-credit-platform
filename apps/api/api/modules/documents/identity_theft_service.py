"""Identity Theft Detection & Recovery service helpers (Phase 8)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.modules.auth.models import User
from api.modules.documents.identity_theft_models import (
    IdentityTheftAccountReview,
    IdentityTheftConfirmation,
    IdentityTheftIncident,
    IdentityTheftIncidentStatus,
    IdentityTheftIssueType,
    IdentityTheftProtectionStatusValue,
    IdentityTheftProtectionType,
)
from api.modules.documents.identity_theft_repository import IdentityTheftRepository
from api.modules.documents.identity_theft_rules import (
    CONSUMER_ATTESTATION_TEXT,
    CONSUMER_CONFIRMATION_OPTIONS,
    DEFAULT_EVIDENCE_CHECKLIST,
    IDENTITY_THEFT_BANNER_BODY,
    IDENTITY_THEFT_BANNER_TITLE,
    RECOVERY_WORKFLOW_STEPS,
    assess_fcra_605b_readiness,
    classification_payload,
    confirmed_identity_theft_classification,
    evaluate_identity_theft,
)
from api.modules.documents.schemas import (
    CaseIdentityTheftFindingsResponse,
    ConfirmIdentityTheftAccountRequest,
    DocumentIdentityTheftFindingsResponse,
    Fcra605bItemResponse,
    Fcra605bReadinessResponse,
    IdentityTheftAccountReviewResponse,
    IdentityTheftCaseCenterResponse,
    IdentityTheftFindingResponse,
    IdentityTheftFindingSummary,
    IdentityTheftIncidentResponse,
    IdentityTheftProtectionResponse,
    UpdateIdentityTheftIncidentRequest,
    UpsertIdentityTheftProtectionRequest,
)


def _finding_response(finding: Any) -> IdentityTheftFindingResponse:
    return IdentityTheftFindingResponse(
        rule_id=finding.rule_id,
        severity=finding.severity,
        title=finding.title,
        description=finding.description,
        detection_source=finding.detection_source,
        issue_type=finding.issue_type,
        confidence=finding.confidence,
        consumer_confirmed=finding.consumer_confirmed,
        legal_path=finding.legal_path,
        ordinary_dispute_locked=finding.ordinary_dispute_locked,
        required_action=finding.required_action,
        classification=classification_payload(finding),
        tradeline_index=finding.tradeline_index,
        creditor_name=finding.creditor_name,
        account_number_masked=finding.account_number_masked,
        fields=list(finding.fields),
        observed=finding.observed,
    )


def identity_theft_document_response(
    *,
    document_id: uuid.UUID,
    bureau: str,
    schema_version: str | None,
    parsed_report: dict[str, Any],
) -> DocumentIdentityTheftFindingsResponse:
    result = evaluate_identity_theft(
        document_id=document_id,
        bureau=bureau,
        parsed_report=parsed_report,
    )
    return DocumentIdentityTheftFindingsResponse(
        document_id=result.document_id,
        bureau=result.bureau,
        schema_version=result.schema_version or schema_version,
        as_of_date=result.as_of_date,
        banner_active=result.banner_active,
        banner_title=result.banner_title,
        banner_body=result.banner_body,
        ordinary_dispute_locked=result.ordinary_dispute_locked,
        summary=IdentityTheftFindingSummary(**result.summary),
        findings=[_finding_response(f) for f in result.findings],
        protections_detected=list(result.protections_detected),
    )


def aggregate_case_identity_theft_findings(
    *,
    case_id: uuid.UUID,
    reports_by_bureau: dict[str, tuple[uuid.UUID, dict[str, Any]]],
) -> CaseIdentityTheftFindingsResponse:
    documents: list[DocumentIdentityTheftFindingsResponse] = []
    for bureau in sorted(reports_by_bureau):
        document_id, parsed_report = reports_by_bureau[bureau]
        schema_version = parsed_report.get("schema_version")
        documents.append(
            identity_theft_document_response(
                document_id=document_id,
                bureau=bureau,
                schema_version=schema_version if isinstance(schema_version, str) else None,
                parsed_report=parsed_report,
            )
        )
    summary = IdentityTheftFindingSummary(
        total=sum(item.summary.total for item in documents),
        high=sum(item.summary.high for item in documents),
        medium=sum(item.summary.medium for item in documents),
        low=sum(item.summary.low for item in documents),
        tradelines_evaluated=sum(item.summary.tradelines_evaluated for item in documents),
        report_level_indicators=sum(item.summary.report_level_indicators for item in documents),
        tradeline_indicators=sum(item.summary.tradeline_indicators for item in documents),
        ordinary_dispute_locked_count=sum(
            item.summary.ordinary_dispute_locked_count for item in documents
        ),
    )
    banner_active = any(item.banner_active for item in documents)
    ordinary_locked = any(item.ordinary_dispute_locked for item in documents)
    return CaseIdentityTheftFindingsResponse(
        case_id=case_id,
        reports_evaluated=sorted(reports_by_bureau),
        document_ids_by_bureau={
            bureau: document_id for bureau, (document_id, _) in reports_by_bureau.items()
        },
        banner_active=banner_active,
        banner_title=IDENTITY_THEFT_BANNER_TITLE if banner_active else None,
        banner_body=IDENTITY_THEFT_BANNER_BODY if banner_active else None,
        ordinary_dispute_locked=ordinary_locked,
        summary=summary,
        documents=documents,
    )


def _incident_response(incident: IdentityTheftIncident) -> IdentityTheftIncidentResponse:
    return IdentityTheftIncidentResponse(
        id=incident.id,
        case_id=incident.case_id,
        status=incident.status.value,
        discovered_at=incident.discovered_at,
        suspected_theft_period_start=incident.suspected_theft_period_start,
        suspected_theft_period_end=incident.suspected_theft_period_end,
        unrecognized_addresses=list(incident.unrecognized_addresses or []),
        unrecognized_aliases=list(incident.unrecognized_aliases or []),
        companies_contacted=list(incident.companies_contacted or []),
        police_report_number=incident.police_report_number,
        police_report_agency=incident.police_report_agency,
        police_report_filed_at=incident.police_report_filed_at,
        ftc_report_status=incident.ftc_report_status,
        ftc_report_reference=incident.ftc_report_reference,
        evidence_checklist=list(incident.evidence_checklist or []),
        recovery_step=incident.recovery_step,
        consumer_attestation_at=incident.consumer_attestation_at,
        consumer_attestation_text=incident.consumer_attestation_text,
        notes=incident.notes,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
    )


def _review_response(review: IdentityTheftAccountReview) -> IdentityTheftAccountReviewResponse:
    if review.issue_type == IdentityTheftIssueType.CONFIRMED_IDENTITY_THEFT_CLAIM:
        classification = confirmed_identity_theft_classification(
            packet_readiness=review.packet_readiness or 0,
            missing_evidence=[str(x) for x in (review.missing_evidence or [])],
        )
    else:
        classification = {
            "issueType": review.issue_type.value,
            "detectionSource": review.detection_source,
            "confidence": review.confidence,
            "consumerConfirmed": review.consumer_confirmation is not None,
            "legalPath": review.legal_path,
            "ordinaryDisputeLocked": review.ordinary_dispute_locked,
            "requiredAction": (
                "PREPARE_605B"
                if review.legal_path == "FCRA_605B"
                else "CONSUMER_REVIEW"
                if review.ordinary_dispute_locked
                else "CONTINUE_ORDINARY_DISPUTE"
            ),
        }
    return IdentityTheftAccountReviewResponse(
        id=review.id,
        case_id=review.case_id,
        incident_id=review.incident_id,
        account_id=review.account_id,
        document_id=review.document_id,
        bureau=review.bureau,
        tradeline_index=review.tradeline_index,
        match_key=review.match_key,
        creditor_name=review.creditor_name,
        account_number_masked=review.account_number_masked,
        detection_source=review.detection_source,
        rule_id=review.rule_id,
        confidence=review.confidence,
        issue_type=review.issue_type.value,
        consumer_confirmation=(
            review.consumer_confirmation.value if review.consumer_confirmation else None
        ),
        consumer_confirmed_at=review.consumer_confirmed_at,
        ordinary_dispute_locked=review.ordinary_dispute_locked,
        legal_path=review.legal_path,
        packet_readiness=review.packet_readiness,
        missing_evidence=list(review.missing_evidence or []),
        attestation_accepted=review.attestation_accepted,
        classification=classification,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def _protection_response(row: Any) -> IdentityTheftProtectionResponse:
    return IdentityTheftProtectionResponse(
        id=row.id,
        case_id=row.case_id,
        protection_type=row.protection_type.value,
        status=row.status.value,
        placed_at=row.placed_at,
        expires_at=row.expires_at,
        source=row.source,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _605b_from_incident(incident: IdentityTheftIncident | None) -> Fcra605bReadinessResponse:
    checklist = {
        str(item.get("item_id")): item
        for item in (incident.evidence_checklist if incident else [])
        if isinstance(item, dict)
    }

    def _flag(item_id: str) -> bool | None:
        item = checklist.get(item_id)
        if not isinstance(item, dict):
            return None
        status_value = item.get("status")
        if status_value == "present":
            return True
        if status_value == "missing":
            return False
        return None

    readiness = assess_fcra_605b_readiness(
        has_proof_of_identity=_flag("GOVERNMENT_ID") or _flag("PROOF_OF_IDENTITY"),
        has_identity_theft_report=_flag("FTC_IDENTITY_THEFT_REPORT"),
        has_identified_fraudulent_info=_flag("CREDIT_REPORT_PAGES")
        or _flag("IDENTIFIED_FRAUDULENT_TRADELINES"),
        has_consumer_statement=bool(incident and incident.consumer_attestation_at),
        has_proof_of_address=_flag("PROOF_OF_ADDRESS"),
        has_supporting_creditor_records=_flag("ACCOUNT_STATEMENTS")
        or _flag("SUPPORTING_CREDITOR_RECORDS"),
    )
    return Fcra605bReadinessResponse(
        remedy_type=readiness.remedy_type,
        not_ordinary_dispute=readiness.not_ordinary_dispute,
        packet_readiness=readiness.packet_readiness,
        items=[
            Fcra605bItemResponse(
                item_id=item.item_id,
                label=item.label,
                required=item.required,
                status=item.status,
            )
            for item in readiness.items
        ],
        missing_evidence=list(readiness.missing_evidence),
    )


def fcra_605b_readiness_for_incident(
    incident: IdentityTheftIncident | None,
) -> Fcra605bReadinessResponse:
    """Public wrapper used by §605B packet export."""
    return _605b_from_incident(incident)


async def build_case_center(
    *,
    repo: IdentityTheftRepository,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    findings: CaseIdentityTheftFindingsResponse | None,
) -> IdentityTheftCaseCenterResponse:
    incident = await repo.get_incident_for_case(
        organization_id=organization_id,
        case_id=case_id,
    )
    reviews = await repo.list_account_reviews(
        organization_id=organization_id,
        case_id=case_id,
    )
    protections = await repo.list_protections(
        organization_id=organization_id,
        case_id=case_id,
    )
    banner_active = bool(findings and findings.banner_active)
    return IdentityTheftCaseCenterResponse(
        case_id=case_id,
        disclaimer=(
            "Identity-theft indicators are investigator aids. The platform never "
            "automatically labels an account as identity theft or generates a sworn "
            "claim without consumer confirmation and attestation."
        ),
        confirmation_options=list(CONSUMER_CONFIRMATION_OPTIONS),
        attestation_text=CONSUMER_ATTESTATION_TEXT,
        recovery_workflow_steps=[dict(step) for step in RECOVERY_WORKFLOW_STEPS],
        default_evidence_checklist=[dict(item) for item in DEFAULT_EVIDENCE_CHECKLIST],
        banner_active=banner_active,
        banner_title=findings.banner_title if findings else None,
        banner_body=findings.banner_body if findings else None,
        findings=findings,
        incident=_incident_response(incident) if incident else None,
        account_reviews=[_review_response(r) for r in reviews],
        protections=[_protection_response(p) for p in protections],
        fcra_605b=_605b_from_incident(incident) if incident else None,
    )


async def confirm_account_review(
    *,
    repo: IdentityTheftRepository,
    actor_id: uuid.UUID | None,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    request: ConfirmIdentityTheftAccountRequest,
) -> IdentityTheftAccountReviewResponse:
    confirmation = IdentityTheftConfirmation(request.confirmation)
    now = datetime.now(UTC)

    if (
        confirmation == IdentityTheftConfirmation.IDENTITY_THEFT
        and not request.attestation_accepted
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Consumer attestation is required before opening an identity-theft case. "
                f"Attestation: {CONSUMER_ATTESTATION_TEXT}"
            ),
        )

    unlock_choices = {
        IdentityTheftConfirmation.RECOGNIZE,
        IdentityTheftConfirmation.INACCURATE_REPORTING,
        IdentityTheftConfirmation.AUTHORIZED_USER,
        IdentityTheftConfirmation.MIXED_FILE,
    }
    keep_locked_choices = {
        IdentityTheftConfirmation.NEED_MORE_INFO,
        IdentityTheftConfirmation.UNSURE,
        IdentityTheftConfirmation.IDENTITY_THEFT,
    }

    ordinary_locked = confirmation in keep_locked_choices
    if confirmation in unlock_choices:
        ordinary_locked = False

    incident: IdentityTheftIncident | None = None
    issue_type = IdentityTheftIssueType.IDENTITY_THEFT_INDICATOR
    legal_path: str | None = None
    packet_readiness: int | None = None
    missing_evidence: list[Any] = []

    if confirmation == IdentityTheftConfirmation.IDENTITY_THEFT:
        issue_type = IdentityTheftIssueType.CONFIRMED_IDENTITY_THEFT_CLAIM
        legal_path = "FCRA_605B"
        ordinary_locked = True
        incident = await repo.get_open_incident_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        if incident is None:
            checklist = [{**item, "status": "unknown"} for item in DEFAULT_EVIDENCE_CHECKLIST]
            incident = IdentityTheftIncident(
                id=uuid.uuid4(),
                organization_id=organization_id,
                case_id=case_id,
                status=IdentityTheftIncidentStatus.OPEN,
                discovered_at=request.discovered_at,
                unrecognized_addresses=[],
                unrecognized_aliases=[],
                companies_contacted=[],
                ftc_report_status="not_started",
                evidence_checklist=checklist,
                recovery_step=1,
                consumer_attestation_at=now,
                consumer_attestation_text=CONSUMER_ATTESTATION_TEXT,
            )
            apply_audit_on_create(incident, actor_id)
            incident = await repo.create_incident(incident)
        readiness = _605b_from_incident(incident)
        packet_readiness = readiness.packet_readiness
        missing_evidence = list(readiness.missing_evidence)

    existing = await repo.find_review_by_match(
        organization_id=organization_id,
        case_id=case_id,
        match_key=request.match_key,
        account_id=request.account_id,
        bureau=request.bureau,
        tradeline_index=request.tradeline_index,
    )
    if existing is None:
        review = IdentityTheftAccountReview(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=case_id,
            incident_id=incident.id if incident else None,
            account_id=request.account_id,
            document_id=request.document_id,
            bureau=request.bureau,
            tradeline_index=request.tradeline_index,
            match_key=request.match_key,
            creditor_name=request.creditor_name,
            account_number_masked=request.account_number_masked,
            detection_source=request.detection_source,
            rule_id=request.rule_id,
            confidence=request.confidence,
            issue_type=issue_type,
            consumer_confirmation=confirmation,
            consumer_confirmed_at=now,
            ordinary_dispute_locked=ordinary_locked,
            legal_path=legal_path,
            packet_readiness=packet_readiness,
            missing_evidence=missing_evidence,
            attestation_accepted=request.attestation_accepted,
        )
        apply_audit_on_create(review, actor_id)
        review = await repo.add_account_review(review)
    else:
        existing.incident_id = incident.id if incident else existing.incident_id
        existing.account_id = request.account_id or existing.account_id
        existing.document_id = request.document_id or existing.document_id
        existing.bureau = request.bureau or existing.bureau
        existing.tradeline_index = (
            request.tradeline_index
            if request.tradeline_index is not None
            else existing.tradeline_index
        )
        existing.match_key = request.match_key or existing.match_key
        existing.creditor_name = request.creditor_name or existing.creditor_name
        existing.account_number_masked = (
            request.account_number_masked or existing.account_number_masked
        )
        existing.detection_source = request.detection_source
        existing.rule_id = request.rule_id or existing.rule_id
        existing.confidence = request.confidence
        existing.issue_type = issue_type
        existing.consumer_confirmation = confirmation
        existing.consumer_confirmed_at = now
        existing.ordinary_dispute_locked = ordinary_locked
        existing.legal_path = legal_path
        existing.packet_readiness = packet_readiness
        existing.missing_evidence = missing_evidence
        existing.attestation_accepted = request.attestation_accepted
        apply_audit_on_update(existing, actor_id)
        review = existing

    return _review_response(review)


async def upsert_protection(
    *,
    repo: IdentityTheftRepository,
    user: User,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    request: UpsertIdentityTheftProtectionRequest,
) -> IdentityTheftProtectionResponse:
    row = await repo.upsert_protection(
        organization_id=organization_id,
        case_id=case_id,
        protection_type=IdentityTheftProtectionType(request.protection_type),
        status=IdentityTheftProtectionStatusValue(request.status),
        placed_at=request.placed_at,
        expires_at=request.expires_at,
        source="staff_recorded",
        notes=request.notes,
        user_id=user.id,
    )
    return _protection_response(row)


async def update_incident(
    *,
    repo: IdentityTheftRepository,
    user: User,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    request: UpdateIdentityTheftIncidentRequest,
) -> IdentityTheftIncidentResponse:
    incident = await repo.get_incident_for_case(
        organization_id=organization_id,
        case_id=case_id,
    )
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity theft incident not found for this case",
        )
    if request.status is not None:
        incident.status = IdentityTheftIncidentStatus(request.status)
    for field in (
        "discovered_at",
        "suspected_theft_period_start",
        "suspected_theft_period_end",
        "unrecognized_addresses",
        "unrecognized_aliases",
        "companies_contacted",
        "police_report_number",
        "police_report_agency",
        "police_report_filed_at",
        "ftc_report_status",
        "ftc_report_reference",
        "evidence_checklist",
        "recovery_step",
        "notes",
    ):
        value = getattr(request, field)
        if value is not None:
            setattr(incident, field, value)
    apply_audit_on_update(incident, user.id)
    return _incident_response(incident)
