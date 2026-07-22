"""Account management service — business logic and intelligence."""

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Literal, cast

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.events import publish_platform_event
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.cross_bureau import (
    BureauTradelineView,
    CrossBureauEvidence,
    detect_cross_bureau_discrepancies,
)
from api.modules.accounts.dispute_drafts import (
    CRA_TEMPLATE_ID,
    FURNISHER_TEMPLATE_ID,
    DisputeRecipientType,
    build_dispute_body,
    build_dispute_reason_suggestions,
    build_dispute_reasons,
    build_evidence_checklist,
    build_furnisher_dispute_body,
    build_furnisher_evidence_checklist,
    detect_missing_evidence,
)
from api.modules.accounts.dispute_legal_references import (
    SelectedLegalReference,
    candidates_from_fcra_documents,
    select_best_legal_reference,
)
from api.modules.accounts.dispute_letter_export import (
    DisputeLetterExportFormat,
    build_dispute_letter_export,
)
from api.modules.accounts.dispute_letter_mail_export import (
    DisputeMailExportFormat,
    build_mail_export,
    build_mail_export_context,
)
from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.dispute_letter_repository import DisputeLetterRepository
from api.modules.accounts.dispute_mail_addresses import normalize_consumer_address_lines
from api.modules.accounts.dispute_mail_attachments import (
    ResolvedMailPacketAttachments,
    resolve_mail_packet_attachments,
)
from api.modules.accounts.dispute_response_models import (
    DisputeResponse,
    DisputeResponseMethod,
    DisputeResponseOutcome,
)
from api.modules.accounts.dispute_response_repository import DisputeResponseRepository
from api.modules.accounts.intelligence import apply_account_intelligence, recommend_next_action
from api.modules.accounts.intelligence_calibration import DiscrepancyScoringContext
from api.modules.accounts.intelligence_context import (
    build_discrepancy_context_map,
    compare_case_reports,
    cross_bureau_summary_payload,
    discrepancy_context_for_account,
)
from api.modules.accounts.litigation_packet import (
    LitigationReadinessInputs,
    build_litigation_readiness,
)
from api.modules.accounts.litigation_packet_export import (
    LitigationPacketExportFormat,
    build_litigation_packet_export,
)
from api.modules.accounts.models import Account, DisputeStatus, InvestigationStatus
from api.modules.accounts.permissions import ACCOUNT_DELETE_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.redispute_readiness import compute_redispute_readiness
from api.modules.accounts.reinvestigation import (
    compute_reinvestigation_clock,
    document_extends_window,
)
from api.modules.accounts.repository import AccountListFilters, AccountRepository
from api.modules.accounts.schemas import (
    AccountCreate,
    AccountDisputeDraftResponse,
    AccountDisputeResponseReceivedRequest,
    AccountIntelligenceSummary,
    AccountListParams,
    AccountLitigationPacket,
    AccountRedisputeReadiness,
    AccountReinvestigationClock,
    AccountReinvestigationRecipientClock,
    AccountResponse,
    AccountUpdate,
    CaseRedisputeReadinessResponse,
    CaseRedisputeReadinessSummary,
    CaseReinvestigationClockResponse,
    CaseReinvestigationClockSummary,
    CaseReinvestigationSummary,
    CrossBureauIntelligenceSummary,
    DisputeLetterResponse,
    DisputeReasonSuggestionResponse,
    DisputeResponseRecordOutcome,
    DisputeResponseRecordResponse,
    LitigationCrossBureauDiscrepancy,
    LitigationCrossBureauEvidence,
    LitigationPacketLetter,
    LitigationPacketResponse,
    LitigationReadinessAssessment,
    MissingEvidenceResponse,
    NextActionItem,
    RecordDisputeResponseRequest,
)
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.compliance.consent_gates import require_signed_consents
from api.modules.compliance.repository import ConsentRepository
from api.modules.documents.repository import DocumentRepository
from api.modules.documents.storage import DocumentStorage, get_document_storage
from api.modules.org_admin.cross_bureau_tolerance import resolve_cross_bureau_balance_tolerance
from api.modules.tasks.models import Task, TaskPriority
from api.modules.tasks.repository import TaskRepository
from api.modules.tasks.schemas import TaskResponse
from api.modules.timeline.builders import (
    account_created_event,
    account_dispute_status_changed_event,
    account_investigation_overdue_event,
    account_status_changed_event,
    account_updated_event,
    dispute_letter_approved_event,
    dispute_letter_draft_created_event,
    dispute_letter_sent_event,
    dispute_letter_voided_event,
    task_created_event,
)
from api.repositories.account import AccountRepositoryProtocol

DISPUTE_DRAFT_REVIEW_TASK_SOURCE = "accounts.dispute_draft"
DISPUTE_LETTER_REVIEW_TASK_SOURCE = "accounts.dispute_letter"
DISPUTE_LETTER_FOLLOWUP_TASK_SOURCE = "accounts.dispute_letter_followup"
DISPUTE_INVESTIGATION_OVERDUE_TASK_SOURCE = "accounts.dispute_investigation_overdue"
DISPUTE_LETTER_CRA_RESPONSE_DAYS = 30
_DISPUTE_RESPONSE_OUTCOMES: dict[str, DisputeStatus] = {
    "verified": DisputeStatus.VERIFIED,
    "corrected": DisputeStatus.CORRECTED,
    "deleted": DisputeStatus.DELETED,
}
_VOIDABLE_DISPUTE_LETTER_STATUSES = frozenset(
    {
        DisputeLetterStatus.DRAFT,
        DisputeLetterStatus.REVIEW,
        DisputeLetterStatus.APPROVED,
    }
)


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        case_repo: CaseRepository | None = None,
        task_repo: TaskRepository | None = None,
        dispute_letter_repo: DisputeLetterRepository | None = None,
        session: AsyncSession | None = None,
        storage: DocumentStorage | None = None,
    ) -> None:
        self._accounts = account_repo
        self._cases = case_repo
        self._tasks = task_repo
        self._dispute_letters = dispute_letter_repo
        self._session = session
        self._storage = storage or get_document_storage()

    @classmethod
    def from_session(cls, session: AsyncSession) -> "AccountService":
        return cls(
            AccountRepository(session),
            CaseRepository(session),
            TaskRepository(session),
            DisputeLetterRepository(session),
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
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify accounts",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete accounts",
            )

    async def _discrepancy_context_for_account(
        self,
        account: Account,
    ) -> DiscrepancyScoringContext | None:
        if self._session is None:
            return None

        document_repo = DocumentRepository(self._session)
        parsed_reports = await document_repo.list_case_parsed_credit_reports(
            organization_id=account.organization_id,
            case_id=account.case_id,
        )
        reports_by_bureau: dict[str, tuple[uuid.UUID, dict[str, object]]] = {}
        for parsed_report in parsed_reports:
            bureau = str(parsed_report.bureau).lower()
            if bureau in reports_by_bureau:
                continue
            reports_by_bureau[bureau] = (parsed_report.document_id, parsed_report.parsed_report)
        if len(reports_by_bureau) < 2:
            return None

        result = compare_case_reports(
            case_id=account.case_id,
            reports_by_bureau=reports_by_bureau,
        )
        context_map = build_discrepancy_context_map(result.discrepancies)
        return discrepancy_context_for_account(account, context_map)

    async def _apply_intelligence(self, account: Account) -> None:
        use_ml = is_feature_enabled(FeatureFlag.ENABLE_ML_SCORING) and is_feature_enabled(
            FeatureFlag.ENABLE_AI
        )
        discrepancy = await self._discrepancy_context_for_account(account) if use_ml else None
        apply_account_intelligence(
            account,
            discrepancy_context=discrepancy,
            use_ml_calibration=use_ml,
        )

    async def _cross_bureau_intelligence_summary(
        self,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> CrossBureauIntelligenceSummary | None:
        if self._session is None:
            return None

        document_repo = DocumentRepository(self._session)
        parsed_reports = await document_repo.list_case_parsed_credit_reports(
            organization_id=organization_id,
            case_id=case_id,
        )
        reports_by_bureau: dict[str, tuple[uuid.UUID, dict[str, object]]] = {}
        for parsed_report in parsed_reports:
            bureau = str(parsed_report.bureau).lower()
            if bureau in reports_by_bureau:
                continue
            reports_by_bureau[bureau] = (parsed_report.document_id, parsed_report.parsed_report)
        if len(reports_by_bureau) < 2:
            return CrossBureauIntelligenceSummary(available=False)

        result = compare_case_reports(case_id=case_id, reports_by_bureau=reports_by_bureau)
        summary = cross_bureau_summary_payload(result.summary)
        return CrossBureauIntelligenceSummary(
            available=True,
            reports_compared=list(result.reports_compared),
            actionable_discrepancies=summary["actionable_discrepancies"],
            dispute_ready_discrepancies=summary["dispute_ready_discrepancies"],
            investigation_needed=summary["investigation_needed"],
            consistent_tradelines=summary["consistent_tradelines"],
            total_tradelines=summary["total_tradelines"],
        )

    async def _validate_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        if self._cases is None:
            return
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case must belong to the same organization",
            )

    async def _get_account_for_user(self, account_id: uuid.UUID, user: User) -> Account:
        organization_id = self._require_organization(user)
        account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return account

    @staticmethod
    def _filters_from_params(
        organization_id: uuid.UUID,
        params: AccountListParams,
    ) -> AccountListFilters:
        return AccountListFilters(
            organization_id=organization_id,
            search=params.search,
            case_id=params.case_id,
            client_id=params.client_id,
            bureau=params.bureau,
            account_type=params.account_type,
            account_status=params.account_status,
            payment_status=params.payment_status,
            dispute_status=params.dispute_status,
            min_risk_score=params.min_risk_score,
            max_risk_score=params.max_risk_score,
            min_readiness_score=params.min_readiness_score,
            dispute_ready=params.dispute_ready,
            skip=params.offset,
            limit=params.page_size,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )

    async def create_account(self, user: User, data: AccountCreate) -> AccountResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._validate_case(data.case_id, organization_id)

        account = Account(
            organization_id=organization_id,
            case_id=data.case_id,
            bureau=data.bureau,
            creditor_name=data.creditor_name,
            original_creditor=data.original_creditor,
            account_number_masked=data.account_number_masked,
            account_type=data.account_type,
            account_status=data.account_status,
            payment_status=data.payment_status,
            balance=data.balance,
            high_balance=data.high_balance,
            credit_limit=data.credit_limit,
            monthly_payment=data.monthly_payment,
            past_due_amount=data.past_due_amount,
            date_opened=data.date_opened,
            date_reported=data.date_reported,
            date_last_activity=data.date_last_activity,
            date_first_delinquency=data.date_first_delinquency,
            estimated_removal_date=data.estimated_removal_date,
            responsibility=data.responsibility,
            remarks=data.remarks,
            dispute_round=data.dispute_round,
            investigation_status=data.investigation_status,
            last_dispute_date=data.last_dispute_date,
            response_received=data.response_received,
            cra_dispute=data.cra_dispute,
            furnisher_dispute=data.furnisher_dispute,
            cfpb_dispute=data.cfpb_dispute,
            ai_summary=data.ai_summary,
            ai_recommended_next_action=data.ai_recommended_next_action,
        )
        if data.dispute_status is not None:
            account.dispute_status = data.dispute_status

        await self._apply_intelligence(account)
        apply_audit_on_create(account, user.id)
        created = await self._accounts.create(account)
        if self._session is not None:
            await publish_platform_event(self._session, account_created_event(created, user.id))
        return AccountResponse.from_model(created)

    async def list_accounts(
        self,
        user: User,
        params: AccountListParams,
    ) -> PaginatedResponse[AccountResponse]:
        organization_id = self._require_organization(user)
        filters = self._filters_from_params(organization_id, params)
        items, total = await self._accounts.list_accounts(filters)
        return paginate(
            [AccountResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def list_case_accounts(
        self,
        user: User,
        case_id: uuid.UUID,
        params: AccountListParams,
    ) -> PaginatedResponse[AccountResponse]:
        organization_id = self._require_organization(user)
        await self._validate_case(case_id, organization_id)
        scoped = params.model_copy(update={"case_id": case_id})
        return await self.list_accounts(user, scoped)

    async def list_client_accounts(
        self,
        user: User,
        client_id: uuid.UUID,
        params: AccountListParams,
    ) -> PaginatedResponse[AccountResponse]:
        scoped = params.model_copy(update={"client_id": client_id})
        return await self.list_accounts(user, scoped)

    @staticmethod
    def _cra_response_deadline_passed(account: Account) -> bool:
        if account.last_dispute_date is None:
            return False
        deadline = account.last_dispute_date + timedelta(days=DISPUTE_LETTER_CRA_RESPONSE_DAYS)
        return date.today() > deadline

    async def get_account(self, user: User, account_id: uuid.UUID) -> AccountResponse:
        account = await self._get_account_for_user(account_id, user)
        return AccountResponse.from_model(account)

    async def get_dispute_draft(
        self,
        user: User,
        account_id: uuid.UUID,
        *,
        recipient_type: DisputeRecipientType = "credit_bureau",
    ) -> AccountDisputeDraftResponse:
        account = await self._get_account_for_user(account_id, user)
        if self._cases is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Case repository is not configured",
            )
        case = await self._cases.get_by_id(
            account.case_id,
            organization_id=account.organization_id,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        disputed_items = build_dispute_reasons(account)
        reason_suggestions = build_dispute_reason_suggestions(account)
        legal_ref = await self._select_legal_reference_for_account(
            user,
            account,
            recipient_type=recipient_type,
        )
        if recipient_type == "furnisher":
            evidence_checklist = build_furnisher_evidence_checklist(account)
            template_id = FURNISHER_TEMPLATE_ID
            subject = f"Direct furnisher dispute — {account.creditor_name} tradeline"
            body = build_furnisher_dispute_body(
                account,
                case,
                disputed_items,
                legal_pursuant=legal_ref.pursuant_clause,
            )
            requested_action = (
                "Investigate the consumer's direct furnisher dispute, correct or delete "
                "unverifiable information, and notify all CRAs to whom you furnish data."
            )
            compliance_notes = [
                "Draft requires staff review before sending.",
                "Confirm consumer authorization and supporting evidence before submission.",
                "Direct furnisher disputes must be sent to the data furnisher, not the CRA.",
            ]
        else:
            evidence_checklist = build_evidence_checklist(account)
            template_id = CRA_TEMPLATE_ID
            subject = f"Dispute of {account.creditor_name} tradeline"
            body = build_dispute_body(
                account,
                case,
                disputed_items,
                legal_pursuant=legal_ref.pursuant_clause,
            )
            requested_action = (
                "Investigate the disputed tradeline and delete or correct any information "
                "that cannot be verified as complete and accurate."
            )
            compliance_notes = [
                "Draft requires staff review before sending.",
                "Confirm consumer authorization and supporting evidence before submission.",
            ]

        if legal_ref.source == "finding" and legal_ref.source_rule_id:
            compliance_notes.append(
                "Legal references selected from strongest matched FCRA finding "
                f"(`{legal_ref.source_rule_id}`). Investigator aid only — not legal advice."
            )
        else:
            compliance_notes.append(
                "Legal references use the default procedural FCRA dispute right "
                "(§611 CRA / §623 furnisher). No matched FCRA finding sections were available."
            )

        missing_evidence = detect_missing_evidence(
            account,
            case,
            evidence_checklist=evidence_checklist,
            reason_suggestions=reason_suggestions,
        )
        return AccountDisputeDraftResponse(
            account_id=account.id,
            case_id=account.case_id,
            bureau=account.bureau,
            recipient_type=recipient_type,
            template_id=template_id,
            subject=subject,
            body=body,
            disputed_items=disputed_items,
            dispute_reason_suggestions=[
                DisputeReasonSuggestionResponse(
                    code=suggestion.code,
                    category=suggestion.category,
                    title=suggestion.title,
                    description=suggestion.description,
                    severity=suggestion.severity,
                    requires_evidence=list(suggestion.requires_evidence),
                )
                for suggestion in reason_suggestions
            ],
            requested_action=requested_action,
            evidence_checklist=evidence_checklist,
            compliance_notes=compliance_notes,
            evidence_ready=not missing_evidence,
            missing_evidence=[
                MissingEvidenceResponse(
                    code=item.code,
                    title=item.title,
                    description=item.description,
                    severity=item.severity,
                    checklist_item=item.checklist_item,
                )
                for item in missing_evidence
            ],
            generated_by="rules",
            readiness_score=account.readiness_score,
            risk_score=account.risk_score,
            legal_citations=list(legal_ref.citations),
            legal_reference_source=legal_ref.source,
            legal_reference_rule_id=legal_ref.source_rule_id,
            legal_pursuant=legal_ref.pursuant_clause,
        )

    async def create_dispute_letter_draft(
        self,
        user: User,
        account_id: uuid.UUID,
        *,
        recipient_type: DisputeRecipientType = "credit_bureau",
    ) -> DisputeLetterResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        # Pause ordinary dispute generation when identity theft is suspected/confirmed.
        from api.modules.documents.service import DocumentService as _DocService

        if self._session is not None:
            doc_service = _DocService.from_session(self._session)
            await doc_service.assert_ordinary_dispute_allowed_for_account(
                user,
                case_id=account.case_id,
                account_id=account.id,
                creditor_name=account.creditor_name,
                account_number_masked=account.account_number_masked,
            )
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )
        draft = await self.get_dispute_draft(
            user,
            account_id,
            recipient_type=recipient_type,
        )
        now = datetime.now(UTC)
        dispute_letter = DisputeLetter(
            organization_id=account.organization_id,
            case_id=account.case_id,
            account_id=account.id,
            recipient_type=draft.recipient_type,
            status=DisputeLetterStatus.DRAFT,
            template_id=draft.template_id,
            subject=draft.subject,
            body=draft.body,
            disputed_items=draft.disputed_items,
            requested_action=draft.requested_action,
            evidence_checklist=draft.evidence_checklist,
            compliance_notes=draft.compliance_notes,
            generated_by=draft.generated_by,
            generated_at=now,
        )
        apply_audit_on_create(dispute_letter, user.id)
        created = await self._dispute_letters.create(dispute_letter)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                dispute_letter_draft_created_event(created, user.id),
            )
        return DisputeLetterResponse.from_model(created)

    async def list_dispute_letters(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> list[DisputeLetterResponse]:
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )
        letters = await self._dispute_letters.list_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
        )
        return [DisputeLetterResponse.from_model(letter) for letter in letters]

    async def get_dispute_letter(
        self,
        user: User,
        account_id: uuid.UUID,
        letter_id: uuid.UUID,
    ) -> DisputeLetterResponse:
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        dispute_letter = await self._dispute_letters.get_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
            letter_id=letter_id,
        )
        if dispute_letter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute letter not found",
            )
        return DisputeLetterResponse.from_model(dispute_letter)

    async def _get_case_for_account(self, account: Account) -> Case:
        if self._cases is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Case repository is not configured",
            )
        case = await self._cases.get_by_id(account.case_id, organization_id=account.organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case

    async def _require_dispute_mail_consents(self, case: Case) -> None:
        if case.client_id is None or self._session is None:
            return
        await require_signed_consents(
            ConsentRepository(self._session),
            organization_id=case.organization_id,
            client_id=case.client_id,
        )

    async def export_dispute_letter(
        self,
        user: User,
        account_id: uuid.UUID,
        letter_id: uuid.UUID,
        *,
        export_format: DisputeLetterExportFormat | DisputeMailExportFormat,
    ) -> tuple[bytes, str, str]:
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        dispute_letter = await self._dispute_letters.get_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
            letter_id=letter_id,
        )
        if dispute_letter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute letter not found",
            )

        if export_format in {"mail-letter", "mail-label", "mail-packet", "report-excerpt"}:
            case = await self._get_case_for_account(account)
            await self._require_dispute_mail_consents(case)

        if export_format == "report-excerpt":
            return await self._export_dispute_report_excerpt(account=account)

        if export_format in {"mail-letter", "mail-label", "mail-packet"}:
            return await self._build_mail_letter_export(
                user=user,
                account=account,
                dispute_letter=dispute_letter,
                export_format=cast(DisputeMailExportFormat, export_format),
            )

        if export_format in {"text", "pdf"}:
            return build_dispute_letter_export(
                dispute_letter,
                cast(DisputeLetterExportFormat, export_format),
            )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported export format: {export_format}",
        )

    async def collect_case_mail_packet_files(
        self,
        user: User,
        case_id: uuid.UUID,
        *,
        require_consents: bool = True,
    ) -> list[tuple[str, bytes]]:
        """Build per-account mail-packet PDFs for a case (consent-gated when required)."""
        organization_id = self._require_organization(user)
        case = await self._get_case_by_id(case_id, organization_id)
        if require_consents:
            await self._require_dispute_mail_consents(case)
        consumer_address_lines = await self._resolve_consumer_address_lines(
            organization_id=organization_id,
            case_id=case_id,
        )

        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        packets: list[tuple[str, bytes]] = []
        page = 1
        while True:
            page_result = await self.list_case_accounts(
                user,
                case_id,
                params=AccountListParams(page=page, page_size=100),
            )
            for account_summary in page_result.items:
                account = await self._accounts.get_by_id(
                    account_summary.id,
                    organization_id=organization_id,
                )
                if account is None:
                    continue
                letters = await self._dispute_letters.list_for_account(
                    organization_id=organization_id,
                    account_id=account.id,
                )
                if not letters:
                    continue
                dispute_letter = letters[0]
                legal_ref = await self._select_legal_reference_for_account(
                    user,
                    account,
                    recipient_type=cast(
                        DisputeRecipientType,
                        dispute_letter.recipient_type
                        if dispute_letter.recipient_type in {"credit_bureau", "furnisher"}
                        else "credit_bureau",
                    ),
                )
                context = build_mail_export_context(
                    account=account,
                    case=case,
                    dispute_letter=dispute_letter,
                    consumer_address_lines=consumer_address_lines,
                    legal_pursuant=legal_ref.pursuant_clause,
                )
                attachments = await self._resolve_mail_packet_attachments(
                    organization_id=organization_id,
                    case=case,
                    account=account,
                )
                content, filename, _ = build_mail_export(
                    dispute_letter,
                    context,
                    "mail-packet",
                    attachments=attachments,
                )
                packets.append((filename, content))

            if page >= page_result.pages:
                break
            page += 1

        return packets

    async def export_case_dispute_mail_packets(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> tuple[bytes, str, str]:
        import zipfile
        from io import BytesIO

        packets = await self.collect_case_mail_packet_files(user, case_id)
        if not packets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dispute letter drafts found on this case",
            )

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for filename, content in packets:
                archive.writestr(filename, content)

        short_case_id = str(case_id).split("-", 1)[0]
        return (
            buffer.getvalue(),
            f"case-mail-packets-{short_case_id}.zip",
            "application/zip",
        )

    async def collect_case_report_excerpt_files(
        self,
        user: User,
        case_id: uuid.UUID,
        *,
        require_consents: bool = True,
    ) -> list[tuple[str, bytes]]:
        """Build per-account report-excerpt PDFs for a case (consent-gated when required)."""
        from api.modules.accounts.dispute_mail_attachments import build_account_report_excerpt

        organization_id = self._require_organization(user)
        case = await self._get_case_by_id(case_id, organization_id)
        if require_consents:
            await self._require_dispute_mail_consents(case)

        if self._dispute_letters is None or self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        excerpts: list[tuple[str, bytes]] = []
        page = 1
        while True:
            page_result = await self.list_case_accounts(
                user,
                case_id,
                params=AccountListParams(page=page, page_size=100),
            )
            for account_summary in page_result.items:
                account = await self._accounts.get_by_id(
                    account_summary.id,
                    organization_id=organization_id,
                )
                if account is None:
                    continue
                letters = await self._dispute_letters.list_for_account(
                    organization_id=organization_id,
                    account_id=account.id,
                )
                if not letters:
                    continue

                result = await build_account_report_excerpt(
                    self._session,
                    self._storage,
                    organization_id=organization_id,
                    case_id=case_id,
                    account=account,
                )
                if result is None:
                    continue
                content, filename = result
                excerpts.append((filename, content))

            if page >= page_result.pages:
                break
            page += 1

        return excerpts

    async def export_case_dispute_report_excerpts(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> tuple[bytes, str, str]:
        import zipfile
        from io import BytesIO

        excerpts = await self.collect_case_report_excerpt_files(user, case_id)
        if not excerpts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dispute letter drafts found on this case",
            )

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for filename, content in excerpts:
                archive.writestr(filename, content)

        short_case_id = str(case_id).split("-", 1)[0]
        return (
            buffer.getvalue(),
            f"case-report-excerpts-{short_case_id}.zip",
            "application/zip",
        )

    async def _build_mail_letter_export(
        self,
        *,
        user: User,
        account: Account,
        dispute_letter: DisputeLetter,
        export_format: DisputeMailExportFormat,
    ) -> tuple[bytes, str, str]:
        case = await self._get_case_for_account(account)
        consumer_address_lines = await self._resolve_consumer_address_lines(
            organization_id=account.organization_id,
            case_id=account.case_id,
        )
        recipient_type: DisputeRecipientType = (
            "furnisher" if dispute_letter.recipient_type == "furnisher" else "credit_bureau"
        )
        legal_ref = await self._select_legal_reference_for_account(
            user,
            account,
            recipient_type=recipient_type,
        )
        context = build_mail_export_context(
            account=account,
            case=case,
            dispute_letter=dispute_letter,
            consumer_address_lines=consumer_address_lines,
            legal_pursuant=legal_ref.pursuant_clause,
        )
        attachments = None
        if export_format == "mail-packet":
            attachments = await self._resolve_mail_packet_attachments(
                organization_id=account.organization_id,
                case=case,
                account=account,
            )
        return build_mail_export(
            dispute_letter,
            context,
            export_format,
            attachments=attachments,
        )

    async def _select_legal_reference_for_account(
        self,
        user: User,
        account: Account,
        *,
        recipient_type: DisputeRecipientType,
    ) -> SelectedLegalReference:
        if self._session is None:
            return select_best_legal_reference(recipient_type, ())

        from api.modules.documents.service import DocumentService as _DocService

        doc_service = _DocService.from_session(self._session)
        try:
            fcra = await doc_service.get_case_fcra_findings(user, account.case_id)
        except HTTPException:
            return select_best_legal_reference(recipient_type, ())

        candidates = candidates_from_fcra_documents(
            fcra.documents,
            creditor_name=account.creditor_name,
            account_number_masked=account.account_number_masked,
            bureau=account.bureau.value,
        )
        return select_best_legal_reference(recipient_type, candidates)

    async def _resolve_mail_packet_attachments(
        self,
        *,
        organization_id: uuid.UUID,
        case: Case,
        account: Account,
    ) -> ResolvedMailPacketAttachments:
        if self._session is None:
            return ResolvedMailPacketAttachments(
                identity=None,
                proof_of_address=None,
                credit_report=None,
            )

        return await resolve_mail_packet_attachments(
            self._session,
            self._storage,
            organization_id=organization_id,
            case=case,
            account=account,
        )

    async def _export_dispute_report_excerpt(
        self,
        *,
        account: Account,
    ) -> tuple[bytes, str, str]:
        from api.modules.accounts.dispute_mail_attachments import build_account_report_excerpt

        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )

        result = await build_account_report_excerpt(
            self._session,
            self._storage,
            organization_id=account.organization_id,
            case_id=account.case_id,
            account=account,
        )
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No credit report found for this account bureau",
            )
        content, filename = result
        return content, filename, "application/pdf"

    async def _get_case_by_id(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case:
        if self._cases is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Case repository is not configured",
            )
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case

    async def _resolve_consumer_address_lines(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[str]:
        if self._session is None:
            return []

        from sqlalchemy import select

        from api.modules.documents.metadata_models import DocumentMetadata
        from api.modules.documents.models import Document

        result = await self._session.execute(
            select(DocumentMetadata.addresses)
            .join(Document, Document.id == DocumentMetadata.document_id)
            .where(
                Document.organization_id == organization_id,
                Document.case_id == case_id,
                Document.deleted_at.is_(None),
            )
            .order_by(DocumentMetadata.extracted_at.desc())
            .limit(5)
        )
        for addresses in result.scalars():
            if addresses:
                return normalize_consumer_address_lines([line for line in addresses if line])
        return []

    async def create_dispute_letter_review_task(
        self,
        user: User,
        account_id: uuid.UUID,
        letter_id: uuid.UUID,
    ) -> TaskResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )
        if self._tasks is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task repository is not configured",
            )

        dispute_letter = await self._dispute_letters.get_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
            letter_id=letter_id,
        )
        if dispute_letter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute letter not found",
            )

        existing = await self._tasks.find_active_by_account_source(
            organization_id=account.organization_id,
            account_id=account.id,
            source_module=DISPUTE_LETTER_REVIEW_TASK_SOURCE,
            source_event_id=dispute_letter.id,
        )
        if existing is not None:
            if dispute_letter.status == DisputeLetterStatus.DRAFT:
                dispute_letter.status = DisputeLetterStatus.REVIEW
                apply_audit_on_update(dispute_letter, user.id)
            return TaskResponse.from_model(existing)

        if dispute_letter.status == DisputeLetterStatus.DRAFT:
            dispute_letter.status = DisputeLetterStatus.REVIEW
            apply_audit_on_update(dispute_letter, user.id)

        task = Task(
            organization_id=account.organization_id,
            case_id=account.case_id,
            account_id=account.id,
            title=f"Review saved dispute letter for {account.creditor_name}",
            description=(
                "Review the saved CRA dispute letter draft, confirm supporting evidence, "
                "and prepare the next dispute action."
            ),
            priority=TaskPriority.HIGH,
            due_date=datetime.now(UTC) + timedelta(days=1),
            source_module=DISPUTE_LETTER_REVIEW_TASK_SOURCE,
            source_event_id=dispute_letter.id,
        )
        apply_audit_on_create(task, user.id)
        created = await self._tasks.create(task)
        if self._session is not None:
            await publish_platform_event(self._session, task_created_event(created, user.id))
        return TaskResponse.from_model(created)

    async def _ensure_dispute_letter_followup_task(
        self,
        user: User,
        account: Account,
        dispute_letter: DisputeLetter,
    ) -> None:
        if self._tasks is None:
            return

        existing = await self._tasks.find_active_by_account_source(
            organization_id=account.organization_id,
            account_id=account.id,
            source_module=DISPUTE_LETTER_FOLLOWUP_TASK_SOURCE,
            source_event_id=dispute_letter.id,
        )
        if existing is not None:
            return

        task = Task(
            organization_id=account.organization_id,
            case_id=account.case_id,
            account_id=account.id,
            title=f"Track CRA response for {account.creditor_name}",
            description=(
                "Monitor the CRA investigation timeline after the dispute letter was sent. "
                "Follow up if no response is received within the statutory window."
            ),
            priority=TaskPriority.MEDIUM,
            due_date=datetime.now(UTC) + timedelta(days=DISPUTE_LETTER_CRA_RESPONSE_DAYS),
            source_module=DISPUTE_LETTER_FOLLOWUP_TASK_SOURCE,
            source_event_id=dispute_letter.id,
        )
        apply_audit_on_create(task, user.id)
        created = await self._tasks.create(task)
        if self._session is not None:
            await publish_platform_event(self._session, task_created_event(created, user.id))

    async def _ensure_overdue_investigation_task(
        self,
        user: User,
        account: Account,
    ) -> None:
        if self._tasks is None:
            return

        existing = await self._tasks.find_active_by_account_source(
            organization_id=account.organization_id,
            account_id=account.id,
            source_module=DISPUTE_INVESTIGATION_OVERDUE_TASK_SOURCE,
            source_event_id=account.id,
        )
        if existing is not None:
            return

        task = Task(
            organization_id=account.organization_id,
            case_id=account.case_id,
            account_id=account.id,
            title=f"Escalate overdue CRA investigation for {account.creditor_name}",
            description=(
                "The statutory CRA investigation window has passed without a recorded response. "
                "Escalate with the bureau or furnisher and document next steps."
            ),
            priority=TaskPriority.HIGH,
            due_date=datetime.now(UTC) + timedelta(days=2),
            source_module=DISPUTE_INVESTIGATION_OVERDUE_TASK_SOURCE,
            source_event_id=account.id,
        )
        apply_audit_on_create(task, user.id)
        created = await self._tasks.create(task)
        if self._session is not None:
            await publish_platform_event(self._session, task_created_event(created, user.id))

    async def _maybe_escalate_overdue_investigation(
        self,
        user: User,
        account: Account,
    ) -> Account:
        if not self._should_escalate_overdue_investigation(account):
            return account
        return await self._escalate_overdue_investigation(user, account)

    @staticmethod
    def _should_escalate_overdue_investigation(account: Account) -> bool:
        if account.dispute_status != DisputeStatus.AWAITING_RESPONSE:
            return False
        if account.investigation_status not in (
            InvestigationStatus.PENDING,
            InvestigationStatus.OVERDUE,
        ):
            return False
        return AccountService._cra_response_deadline_passed(account)

    async def _escalate_overdue_investigation(
        self,
        user: User,
        account: Account,
    ) -> Account:
        if account.investigation_status == InvestigationStatus.OVERDUE:
            await self._ensure_overdue_investigation_task(user, account)
            return account

        previous_investigation_status = (
            account.investigation_status.value
            if hasattr(account.investigation_status, "value")
            else account.investigation_status
        )
        account.investigation_status = InvestigationStatus.OVERDUE
        await self._apply_intelligence(account)
        account.ai_recommended_next_action = recommend_next_action(account)
        apply_audit_on_update(account, user.id)
        updated = await self._accounts.update(account)
        await self._ensure_overdue_investigation_task(user, updated)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                account_investigation_overdue_event(
                    updated,
                    user.id,
                    previous_investigation_status=previous_investigation_status,
                ),
            )
        return updated

    async def _apply_dispute_sent_account_state(
        self, account: Account, *, sent_at: datetime
    ) -> None:
        account.dispute_status = DisputeStatus.DISPUTE_SENT
        account.last_dispute_date = sent_at.date()
        account.dispute_round += 1
        account.cra_dispute = True
        await self._apply_intelligence(account)
        account.ai_recommended_next_action = recommend_next_action(account)

    async def approve_dispute_letter(
        self,
        user: User,
        account_id: uuid.UUID,
        letter_id: uuid.UUID,
    ) -> DisputeLetterResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        dispute_letter = await self._dispute_letters.get_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
            letter_id=letter_id,
        )
        if dispute_letter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute letter not found",
            )

        if dispute_letter.status == DisputeLetterStatus.APPROVED:
            return DisputeLetterResponse.from_model(dispute_letter)

        if dispute_letter.status != DisputeLetterStatus.REVIEW:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Dispute letter must be in review before approval",
            )

        dispute_letter.status = DisputeLetterStatus.APPROVED
        apply_audit_on_update(dispute_letter, user.id)
        if self._session is not None:
            await self._session.flush()
            await self._session.refresh(dispute_letter)
            await publish_platform_event(
                self._session,
                dispute_letter_approved_event(dispute_letter, user.id),
            )
        return DisputeLetterResponse.from_model(dispute_letter)

    async def send_dispute_letter(
        self,
        user: User,
        account_id: uuid.UUID,
        letter_id: uuid.UUID,
    ) -> DisputeLetterResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        dispute_letter = await self._dispute_letters.get_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
            letter_id=letter_id,
        )
        if dispute_letter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute letter not found",
            )

        case = await self._get_case_for_account(account)
        await self._require_dispute_mail_consents(case)

        if dispute_letter.status == DisputeLetterStatus.SENT:
            await self._ensure_dispute_letter_followup_task(user, account, dispute_letter)
            return DisputeLetterResponse.from_model(dispute_letter)

        if dispute_letter.status != DisputeLetterStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Dispute letter must be approved before marking as sent",
            )

        now = datetime.now(UTC)
        dispute_letter.status = DisputeLetterStatus.SENT
        dispute_letter.sent_at = now
        apply_audit_on_update(dispute_letter, user.id)
        await self._apply_dispute_sent_account_state(account, sent_at=now)
        apply_audit_on_update(account, user.id)
        await self._accounts.update(account)
        if self._session is not None:
            await self._session.flush()
            await self._session.refresh(dispute_letter)
            await publish_platform_event(
                self._session,
                dispute_letter_sent_event(dispute_letter, user.id),
            )
            await publish_platform_event(self._session, account_updated_event(account, user.id))
        await self._ensure_dispute_letter_followup_task(user, account, dispute_letter)
        return DisputeLetterResponse.from_model(dispute_letter)

    async def void_dispute_letter(
        self,
        user: User,
        account_id: uuid.UUID,
        letter_id: uuid.UUID,
    ) -> DisputeLetterResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._dispute_letters is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        dispute_letter = await self._dispute_letters.get_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
            letter_id=letter_id,
        )
        if dispute_letter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute letter not found",
            )

        if dispute_letter.status == DisputeLetterStatus.VOID:
            return DisputeLetterResponse.from_model(dispute_letter)

        if dispute_letter.status not in _VOIDABLE_DISPUTE_LETTER_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Sent dispute letters cannot be voided",
            )

        dispute_letter.status = DisputeLetterStatus.VOID
        apply_audit_on_update(dispute_letter, user.id)
        if self._session is not None:
            await self._session.flush()
            await self._session.refresh(dispute_letter)
            await publish_platform_event(
                self._session,
                dispute_letter_voided_event(dispute_letter, user.id),
            )
        return DisputeLetterResponse.from_model(dispute_letter)

    async def mark_account_awaiting_dispute_response(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> AccountResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)

        if account.dispute_status == DisputeStatus.AWAITING_RESPONSE:
            return AccountResponse.from_model(account)

        if account.dispute_status != DisputeStatus.DISPUTE_SENT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Account must be in dispute_sent before awaiting response",
            )

        previous_dispute_status = (
            account.dispute_status.value
            if hasattr(account.dispute_status, "value")
            else account.dispute_status
        )
        account.dispute_status = DisputeStatus.AWAITING_RESPONSE
        if account.investigation_status == InvestigationStatus.NONE:
            account.investigation_status = InvestigationStatus.PENDING
        await self._apply_intelligence(account)
        account.ai_recommended_next_action = recommend_next_action(account)
        apply_audit_on_update(account, user.id)
        updated = await self._accounts.update(account)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                account_dispute_status_changed_event(
                    updated,
                    user.id,
                    previous_dispute_status=previous_dispute_status,
                ),
            )
        return AccountResponse.from_model(updated)

    async def record_dispute_response_received(
        self,
        user: User,
        account_id: uuid.UUID,
        data: AccountDisputeResponseReceivedRequest,
    ) -> AccountResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        target_status = _DISPUTE_RESPONSE_OUTCOMES[data.outcome]

        if account.dispute_status == target_status and account.response_received:
            return AccountResponse.from_model(account)

        if account.dispute_status != DisputeStatus.AWAITING_RESPONSE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Account must be awaiting response before recording CRA outcome",
            )

        previous_dispute_status = (
            account.dispute_status.value
            if hasattr(account.dispute_status, "value")
            else account.dispute_status
        )
        account.response_received = True
        account.dispute_status = target_status
        account.investigation_status = InvestigationStatus.COMPLETED
        await self._apply_intelligence(account)
        account.ai_recommended_next_action = recommend_next_action(account)
        apply_audit_on_update(account, user.id)
        updated = await self._accounts.update(account)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                account_dispute_status_changed_event(
                    updated,
                    user.id,
                    previous_dispute_status=previous_dispute_status,
                ),
            )
        return AccountResponse.from_model(updated)

    async def record_dispute_response(
        self,
        user: User,
        account_id: uuid.UUID,
        data: RecordDisputeResponseRequest,
    ) -> DisputeResponseRecordResponse:
        """Persist an auditable bureau/furnisher response record for a sent dispute.

        Staff-entered (mail/portal/phone/email) — the platform never polls a bureau.
        Layered over the ``response_received`` flag: terminal outcomes also sync the
        account dispute status so the reinvestigation lifecycle stays consistent.
        """
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        organization_id = account.organization_id

        dispute_letter_id: uuid.UUID | None = None
        if data.dispute_letter_id is not None:
            letter = await DisputeLetterRepository(self._session).get_for_account(
                organization_id=organization_id,
                account_id=account.id,
                letter_id=data.dispute_letter_id,
            )
            if letter is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dispute letter not found for this account",
                )
            dispute_letter_id = letter.id

        document_id: uuid.UUID | None = None
        if data.document_id is not None:
            document = await DocumentRepository(self._session).get_by_id(
                data.document_id,
                organization_id=organization_id,
            )
            if document is None or getattr(document, "case_id", None) != account.case_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linked document not found for this case",
                )
            document_id = document.id

        outcome = DisputeResponseOutcome(data.outcome)
        method = DisputeResponseMethod(data.response_method)
        record = await DisputeResponseRepository(self._session).create(
            organization_id=organization_id,
            case_id=account.case_id,
            account_id=account.id,
            outcome=outcome,
            response_method=method,
            dispute_letter_id=dispute_letter_id,
            document_id=document_id,
            response_date=data.response_date,
            notes=data.notes,
            recorded_by_id=user.id,
        )

        previous_dispute_status = (
            account.dispute_status.value
            if hasattr(account.dispute_status, "value")
            else account.dispute_status
        )
        self._sync_account_after_dispute_response(account, outcome)
        await self._apply_intelligence(account)
        account.ai_recommended_next_action = recommend_next_action(account)
        apply_audit_on_update(account, user.id)
        updated = await self._accounts.update(account)
        current_dispute_status = (
            updated.dispute_status.value
            if hasattr(updated.dispute_status, "value")
            else updated.dispute_status
        )
        if current_dispute_status != previous_dispute_status:
            await publish_platform_event(
                self._session,
                account_dispute_status_changed_event(
                    updated,
                    user.id,
                    previous_dispute_status=previous_dispute_status,
                ),
            )
        return DisputeResponseRecordResponse.from_model(record)

    def _sync_account_after_dispute_response(
        self,
        account: Account,
        outcome: DisputeResponseOutcome,
    ) -> None:
        terminal = {
            DisputeResponseOutcome.DELETED: DisputeStatus.DELETED,
            DisputeResponseOutcome.VERIFIED: DisputeStatus.VERIFIED,
            DisputeResponseOutcome.CORRECTED: DisputeStatus.CORRECTED,
            DisputeResponseOutcome.UPDATED: DisputeStatus.CORRECTED,
        }
        if outcome in terminal:
            account.response_received = True
            account.dispute_status = terminal[outcome]
            account.investigation_status = InvestigationStatus.COMPLETED
        elif outcome == DisputeResponseOutcome.REJECTED:
            account.response_received = True

    async def list_account_dispute_responses(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> list[DisputeResponseRecordResponse]:
        account = await self._get_account_for_user(account_id, user)
        if self._session is None:
            return []
        rows = await DisputeResponseRepository(self._session).list_for_account(
            organization_id=account.organization_id,
            account_id=account.id,
        )
        return [DisputeResponseRecordResponse.from_model(row) for row in rows]

    async def get_case_reinvestigation_clock(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseReinvestigationClockResponse:
        """Compute the FCRA §611 reinvestigation clock for every account in a case.

        Read-only: classifies each tradeline as awaiting / due-soon / overdue /
        responded / not-sent from its last dispute date and any recorded responses.
        No live bureau contact — purely a computed view over stored data.
        """
        organization_id = self._require_organization(user)
        accounts, _ = await self._accounts.list_by_case(case_id, organization_id, limit=500)

        responses_by_account: dict[uuid.UUID, list[object]] = {}
        if self._session is not None:
            rows = await DisputeResponseRepository(self._session).list_for_case(
                organization_id=organization_id,
                case_id=case_id,
            )
            for row in rows:
                responses_by_account.setdefault(row.account_id, []).append(row)

        rounds_by_account = await self._sent_letter_rounds_by_account(
            organization_id=organization_id, case_id=case_id
        )
        recipient_rounds, letter_recipient = await self._recipient_rounds_by_account(
            organization_id=organization_id, case_id=case_id
        )
        doc_dates_by_account, case_level_doc_dates = await self._case_document_dates(
            organization_id=organization_id, case_id=case_id
        )

        today = date.today()
        entries: list[AccountReinvestigationClock] = []
        summary = CaseReinvestigationClockSummary()
        for account in accounts:
            account_responses = responses_by_account.get(account.id, [])
            has_real_response = account.response_received or any(
                getattr(response, "outcome", None) != DisputeResponseOutcome.NO_RESPONSE
                for response in account_responses
            )
            latest_sent_date, round_count = rounds_by_account.get(account.id, (None, 0))
            clock_start_date = latest_sent_date or account.last_dispute_date
            extended = document_extends_window(
                clock_start_date=clock_start_date,
                document_dates=doc_dates_by_account.get(account.id, []) + case_level_doc_dates,
            )
            clock = compute_reinvestigation_clock(
                last_dispute_date=clock_start_date,
                today=today,
                response_recorded=has_real_response,
                extended=extended,
            )
            recipients = self._build_recipient_clocks(
                recipient_rounds=recipient_rounds.get(account.id, {}),
                account_responses=account_responses,
                letter_recipient=letter_recipient,
                document_dates=doc_dates_by_account.get(account.id, []) + case_level_doc_dates,
                today=today,
            )
            entries.append(
                AccountReinvestigationClock(
                    account_id=account.id,
                    creditor_name=account.creditor_name,
                    dispute_status=account.dispute_status,
                    last_dispute_date=account.last_dispute_date,
                    clock_start_date=clock_start_date,
                    dispute_round_count=round_count,
                    deadline=clock.deadline,
                    days_remaining=clock.days_remaining,
                    state=clock.state,
                    extended=clock.extended,
                    response_received=account.response_received,
                    response_count=len(account_responses),
                    recipients=recipients,
                )
            )
            setattr(summary, clock.state, getattr(summary, clock.state) + 1)
            if clock.extended:
                summary.extended_windows += 1

        state_order = {"overdue": 0, "due_soon": 1, "awaiting": 2, "responded": 3, "not_sent": 4}
        entries.sort(
            key=lambda entry: (
                state_order.get(entry.state, 9),
                entry.days_remaining if entry.days_remaining is not None else 9999,
            )
        )
        return CaseReinvestigationClockResponse(
            case_id=case_id,
            generated_at=datetime.now(UTC),
            summary=summary,
            accounts=entries,
        )

    async def get_case_redispute_readiness(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseRedisputeReadinessResponse:
        """Compute advisory re-dispute / escalation readiness for a case.

        Layered on the §611 clock (slice 3) and recorded responses (slice 2):
        classifies each tradeline's recommended next step (wait / prepare / re-dispute /
        escalate / resolved). Advisory only — never files a dispute or escalation.
        """
        organization_id = self._require_organization(user)
        accounts, _ = await self._accounts.list_by_case(case_id, organization_id, limit=500)

        responses_by_account: dict[uuid.UUID, list[object]] = {}
        if self._session is not None:
            rows = await DisputeResponseRepository(self._session).list_for_case(
                organization_id=organization_id,
                case_id=case_id,
            )
            for row in rows:
                responses_by_account.setdefault(row.account_id, []).append(row)

        rounds_by_account = await self._sent_letter_rounds_by_account(
            organization_id=organization_id, case_id=case_id
        )
        doc_dates_by_account, case_level_doc_dates = await self._case_document_dates(
            organization_id=organization_id, case_id=case_id
        )

        today = date.today()
        entries: list[AccountRedisputeReadiness] = []
        summary = CaseRedisputeReadinessSummary()
        for account in accounts:
            account_responses = responses_by_account.get(account.id, [])
            latest_outcome = self._latest_response_outcome(account, account_responses)
            has_real_response = account.response_received or any(
                getattr(response, "outcome", None) != DisputeResponseOutcome.NO_RESPONSE
                for response in account_responses
            )
            latest_sent_date, round_count = rounds_by_account.get(account.id, (None, 0))
            clock_start_date = latest_sent_date or account.last_dispute_date
            extended = document_extends_window(
                clock_start_date=clock_start_date,
                document_dates=doc_dates_by_account.get(account.id, []) + case_level_doc_dates,
            )
            clock = compute_reinvestigation_clock(
                last_dispute_date=clock_start_date,
                today=today,
                response_recorded=has_real_response,
                extended=extended,
            )
            # Prefer the observed number of sent rounds; fall back to the account counter.
            effective_round = max(round_count, account.dispute_round)
            recommendation = compute_redispute_readiness(
                clock_state=clock.state,
                latest_outcome=latest_outcome,
                dispute_round=effective_round,
                risk_score=account.risk_score,
            )
            entries.append(
                AccountRedisputeReadiness(
                    account_id=account.id,
                    creditor_name=account.creditor_name,
                    dispute_status=account.dispute_status,
                    clock_state=clock.state,
                    latest_outcome=latest_outcome,
                    dispute_round=effective_round,
                    risk_score=account.risk_score,
                    action=recommendation.action,
                    priority=recommendation.priority,
                    reason=recommendation.reason,
                )
            )
            setattr(summary, recommendation.action, getattr(summary, recommendation.action) + 1)
            if recommendation.priority == "high":
                summary.high_priority += 1

        priority_order = {"high": 0, "medium": 1, "low": 2}
        entries.sort(key=lambda entry: priority_order.get(entry.priority, 9))
        return CaseRedisputeReadinessResponse(
            case_id=case_id,
            generated_at=datetime.now(UTC),
            summary=summary,
            accounts=entries,
        )

    async def get_case_reinvestigation_summary(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> CaseReinvestigationSummary:
        """Aggregate the §611 clock, advisory readiness, and recorded responses.

        A single per-case dashboard read model over slices 2–4. Read-only: no
        live bureau contact and no writes.
        """
        clock = await self.get_case_reinvestigation_clock(user, case_id)
        readiness = await self.get_case_redispute_readiness(user, case_id)

        total_accounts = len(clock.accounts)
        disputed_accounts = sum(1 for entry in clock.accounts if entry.clock_start_date is not None)
        total_responses = sum(entry.response_count for entry in clock.accounts)

        # Earliest still-open deadline (awaiting / due-soon) for the "next up" hint.
        upcoming = [
            entry
            for entry in clock.accounts
            if entry.deadline is not None
            and entry.state in ("awaiting", "due_soon")
            and entry.days_remaining is not None
            and entry.days_remaining >= 0
        ]
        upcoming.sort(key=lambda entry: entry.deadline or date.max)
        next_entry = upcoming[0] if upcoming else None

        # Most overdue tradeline (largest elapsed days past the deadline).
        overdue_days: list[int] = []
        for entry in clock.accounts:
            if entry.state == "overdue" and entry.days_remaining is not None:
                overdue_days.append(entry.days_remaining)
        most_overdue_days = abs(min(overdue_days)) if overdue_days else None

        action_items = [entry for entry in readiness.accounts if entry.priority == "high"]

        return CaseReinvestigationSummary(
            case_id=case_id,
            generated_at=datetime.now(UTC),
            total_accounts=total_accounts,
            disputed_accounts=disputed_accounts,
            total_responses=total_responses,
            clock=clock.summary,
            readiness=readiness.summary,
            next_deadline=next_entry.deadline if next_entry else None,
            next_deadline_account_id=next_entry.account_id if next_entry else None,
            next_deadline_creditor=next_entry.creditor_name if next_entry else None,
            most_overdue_days=most_overdue_days,
            action_items=action_items,
        )

    async def get_account_litigation_packet(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> AccountLitigationPacket:
        """Assemble an operator-gated litigation-readiness evidence packet.

        Bundles the tradeline's reinvestigation evidence trail (sent letters,
        recorded responses, §611 clock state) with an advisory willful-noncompliance
        grade for a human attorney to review. Read-only — never drafts pleadings,
        never files, and never transmits to a court, bureau, or attorney.
        """
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to assemble a litigation-readiness packet",
            )
        account = await self._get_account_for_user(account_id, user)
        organization_id = account.organization_id

        letters: list[DisputeLetter] = []
        responses: list[DisputeResponse] = []
        if self._session is not None:
            letters = await DisputeLetterRepository(self._session).list_for_account(
                organization_id=organization_id,
                account_id=account_id,
            )
            responses = await DisputeResponseRepository(self._session).list_for_account(
                organization_id=organization_id,
                account_id=account_id,
            )

        sent_letters = [
            letter
            for letter in letters
            if letter.status == DisputeLetterStatus.SENT and letter.sent_at is not None
        ]
        sent_count = len(sent_letters)
        latest_sent_date = max(
            (letter.sent_at.date() for letter in sent_letters if letter.sent_at is not None),
            default=None,
        )
        clock_start_date = latest_sent_date or account.last_dispute_date

        doc_dates_by_account, case_level_doc_dates = await self._case_document_dates(
            organization_id=organization_id, case_id=account.case_id
        )
        extended = document_extends_window(
            clock_start_date=clock_start_date,
            document_dates=doc_dates_by_account.get(account.id, []) + case_level_doc_dates,
        )
        has_real_response = account.response_received or any(
            getattr(response, "outcome", None) != DisputeResponseOutcome.NO_RESPONSE
            for response in responses
        )
        clock = compute_reinvestigation_clock(
            last_dispute_date=clock_start_date,
            today=date.today(),
            response_recorded=has_real_response,
            extended=extended,
        )

        latest_outcome = self._latest_response_outcome(account, cast("list[object]", responses))
        effective_round = max(sent_count, account.dispute_round)
        recommendation = compute_redispute_readiness(
            clock_state=clock.state,
            latest_outcome=latest_outcome,
            dispute_round=effective_round,
            risk_score=account.risk_score,
        )

        cross_bureau_evidence = await self._build_cross_bureau_evidence(
            account=account,
            latest_outcome=latest_outcome,
            organization_id=organization_id,
        )

        readiness = build_litigation_readiness(
            LitigationReadinessInputs(
                clock_state=clock.state,
                latest_outcome=latest_outcome,
                dispute_round=effective_round,
                risk_score=account.risk_score,
                sent_letter_count=sent_count,
                response_count=len(responses),
                cross_bureau_conflicts=cross_bureau_evidence.conflict_count,
                cross_bureau_outcome_conflict=cross_bureau_evidence.has_outcome_conflict,
            )
        )

        return AccountLitigationPacket(
            account_id=account.id,
            case_id=account.case_id,
            creditor_name=account.creditor_name,
            bureau=account.bureau,
            dispute_status=account.dispute_status,
            dispute_round=effective_round,
            risk_score=account.risk_score,
            generated_at=datetime.now(UTC),
            clock_state=clock.state,
            clock_deadline=clock.deadline,
            clock_extended=clock.extended,
            latest_outcome=latest_outcome,
            recommended_action=recommendation.action,
            assessment=LitigationReadinessAssessment(
                eligible=readiness.eligible,
                strength=readiness.strength,
                score=readiness.score,
                indicators=readiness.indicators,
                summary=readiness.summary,
            ),
            cross_bureau=LitigationCrossBureauEvidence(
                compared_bureaus=cross_bureau_evidence.compared_bureaus,
                discrepancies=[
                    LitigationCrossBureauDiscrepancy(
                        kind=discrepancy.kind,
                        bureau=discrepancy.bureau,
                        detail=discrepancy.detail,
                    )
                    for discrepancy in cross_bureau_evidence.discrepancies
                ],
            ),
            letters=[
                LitigationPacketLetter(
                    id=letter.id,
                    recipient_type=getattr(letter.recipient_type, "value", letter.recipient_type),
                    status=letter.status,
                    subject=letter.subject,
                    disputed_items=list(letter.disputed_items or []),
                    generated_at=letter.generated_at,
                    sent_at=letter.sent_at,
                )
                for letter in letters
            ],
            responses=[
                LitigationPacketResponse(
                    id=response.id,
                    outcome=response.outcome.value,
                    response_method=response.response_method.value,
                    response_date=response.response_date,
                    recorded_at=response.recorded_at,
                    notes=response.notes,
                )
                for response in responses
            ],
            disclaimer=(
                "Advisory evidence bundle for attorney review only. This platform does not "
                "provide legal advice, draft pleadings, file suit, or transmit anything to a "
                "court, bureau, or attorney. A licensed attorney must independently review the "
                "evidence and decide whether to litigate."
            ),
        )

    async def export_litigation_packet(
        self,
        user: User,
        account_id: uuid.UUID,
        *,
        export_format: str = "text",
    ) -> tuple[bytes, str, str]:
        """Render the operator-gated litigation packet as a downloadable document.

        Assembles the packet (which enforces ``case_manager``+ write permission)
        and formats it for a licensed attorney to review. Read-only — the platform
        never files, drafts pleadings, or transmits the document anywhere.
        """
        if export_format not in {"text", "pdf"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only 'text' and 'pdf' export formats are supported for litigation packets",
            )
        packet = await self.get_account_litigation_packet(user, account_id)
        typed_format: LitigationPacketExportFormat = "pdf" if export_format == "pdf" else "text"
        return build_litigation_packet_export(packet, typed_format)

    @staticmethod
    def _creditor_key(account: Account) -> tuple[str, str | None]:
        """Normalized (creditor, masked account number) key for sibling matching."""
        creditor = (account.creditor_name or "").strip().lower()
        number = (account.account_number_masked or "").strip() or None
        return creditor, number

    def _is_cross_bureau_sibling(self, target: Account, candidate: Account) -> bool:
        """True when ``candidate`` is the same creditor tradeline at another bureau.

        Same normalized creditor, a different bureau, and — when both carry a
        masked account number — the same number, so distinct tradelines from the
        same creditor are not conflated.
        """
        if candidate.id == target.id:
            return False
        if candidate.bureau == target.bureau:
            return False
        target_creditor, target_number = self._creditor_key(target)
        cand_creditor, cand_number = self._creditor_key(candidate)
        if not target_creditor or target_creditor != cand_creditor:
            return False
        if target_number is not None and cand_number is not None:
            return target_number == cand_number
        return True

    async def _build_cross_bureau_evidence(
        self,
        *,
        account: Account,
        latest_outcome: str | None,
        organization_id: uuid.UUID,
    ) -> CrossBureauEvidence:
        """Compare a tradeline to the same creditor's copies at other bureaus.

        Read-only: loads the case's tradelines and recorded responses already on
        the platform, reduces each sibling to its latest outcome / reported data,
        and detects divergences (deleted-here-but-verified-there, differing
        balances/statuses). No live bureau contact.
        """
        target_view = BureauTradelineView(
            account_id=account.id,
            bureau=getattr(account.bureau, "value", str(account.bureau)),
            latest_outcome=latest_outcome,
            dispute_status=getattr(account.dispute_status, "value", str(account.dispute_status)),
            account_status=getattr(account.account_status, "value", str(account.account_status)),
            payment_status=getattr(account.payment_status, "value", str(account.payment_status)),
            balance=account.balance,
            past_due_amount=account.past_due_amount,
            date_reported=account.date_reported,
            high_balance=account.high_balance,
            credit_limit=account.credit_limit,
        )
        balance_tolerance = await resolve_cross_bureau_balance_tolerance(
            self._session, organization_id
        )
        if self._session is None:
            return detect_cross_bureau_discrepancies(
                target_view, [], balance_tolerance=balance_tolerance
            )

        case_accounts, _ = await self._accounts.list_by_case(
            account.case_id, organization_id, limit=500
        )
        siblings = [
            candidate
            for candidate in case_accounts
            if self._is_cross_bureau_sibling(account, candidate)
        ]
        if not siblings:
            return detect_cross_bureau_discrepancies(
                target_view, [], balance_tolerance=balance_tolerance
            )

        responses_by_account: dict[uuid.UUID, list[object]] = {}
        rows = await DisputeResponseRepository(self._session).list_for_case(
            organization_id=organization_id,
            case_id=account.case_id,
        )
        for row in rows:
            responses_by_account.setdefault(row.account_id, []).append(row)

        sibling_views = [
            BureauTradelineView(
                account_id=sibling.id,
                bureau=getattr(sibling.bureau, "value", str(sibling.bureau)),
                latest_outcome=self._latest_response_outcome(
                    sibling, responses_by_account.get(sibling.id, [])
                ),
                dispute_status=getattr(
                    sibling.dispute_status, "value", str(sibling.dispute_status)
                ),
                account_status=getattr(
                    sibling.account_status, "value", str(sibling.account_status)
                ),
                payment_status=getattr(
                    sibling.payment_status, "value", str(sibling.payment_status)
                ),
                balance=sibling.balance,
                past_due_amount=sibling.past_due_amount,
                date_reported=sibling.date_reported,
                high_balance=sibling.high_balance,
                credit_limit=sibling.credit_limit,
            )
            for sibling in siblings
        ]
        return detect_cross_bureau_discrepancies(
            target_view, sibling_views, balance_tolerance=balance_tolerance
        )

    async def _sent_letter_rounds_by_account(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> dict[uuid.UUID, tuple[date | None, int]]:
        """Per-account (latest sent `sent_at` date, sent-round count) for a case.

        Keys the §611 clock off each actually-sent dispute letter's `sent_at`
        (the mailed round), so multi-round disputes reflect the newest round's
        deadline instead of the account's single `last_dispute_date`.
        """
        rounds: dict[uuid.UUID, tuple[date | None, int]] = {}
        if self._session is None:
            return rounds
        letters = await DisputeLetterRepository(self._session).list_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        for letter in letters:
            if letter.status != DisputeLetterStatus.SENT or letter.sent_at is None:
                continue
            sent_date = letter.sent_at.date()
            latest_date, count = rounds.get(letter.account_id, (None, 0))
            new_latest = (
                sent_date if latest_date is None or sent_date > latest_date else latest_date
            )
            rounds[letter.account_id] = (new_latest, count + 1)
        return rounds

    async def _recipient_rounds_by_account(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> tuple[dict[uuid.UUID, dict[str, tuple[date | None, int]]], dict[uuid.UUID, str]]:
        """Per-account, per-recipient sent-round data + a letter→recipient map.

        Returns ``(rounds_by_recipient, letter_recipient)`` where
        ``rounds_by_recipient[account_id][recipient_type]`` is the
        ``(latest sent date, sent-round count)`` for that recipient (credit
        bureau vs furnisher), and ``letter_recipient[letter_id]`` maps a sent
        letter to its recipient (used to attribute recorded responses).
        """
        rounds: dict[uuid.UUID, dict[str, tuple[date | None, int]]] = {}
        letter_recipient: dict[uuid.UUID, str] = {}
        if self._session is None:
            return rounds, letter_recipient
        letters = await DisputeLetterRepository(self._session).list_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        for letter in letters:
            if letter.status != DisputeLetterStatus.SENT or letter.sent_at is None:
                continue
            recipient = getattr(letter.recipient_type, "value", letter.recipient_type)
            letter_recipient[letter.id] = recipient
            sent_date = letter.sent_at.date()
            per_recipient = rounds.setdefault(letter.account_id, {})
            latest_date, count = per_recipient.get(recipient, (None, 0))
            new_latest = (
                sent_date if latest_date is None or sent_date > latest_date else latest_date
            )
            per_recipient[recipient] = (new_latest, count + 1)
        return rounds, letter_recipient

    @staticmethod
    def _build_recipient_clocks(
        *,
        recipient_rounds: dict[str, tuple[date | None, int]],
        account_responses: list[object],
        letter_recipient: dict[uuid.UUID, str],
        document_dates: list[date],
        today: date,
    ) -> list[AccountReinvestigationRecipientClock]:
        """Compute independent §611 sub-clocks per recipient for one tradeline.

        A tradeline disputed with both a credit bureau and a furnisher carries
        two deadlines. Responses are attributed to a recipient via the recorded
        response's ``dispute_letter_id`` (which maps to that letter's recipient);
        unlinked responses do not resolve a recipient's clock. The §611(a)(1)(B)
        45-day extended-window flag is computed independently for each recipient
        against that recipient's own ``clock_start_date``.
        """
        recipient_clocks: list[AccountReinvestigationRecipientClock] = []
        # Stable, readable ordering: bureau first, then furnisher, then the rest.
        order = {"credit_bureau": 0, "furnisher": 1}
        for recipient in sorted(recipient_rounds, key=lambda r: (order.get(r, 9), r)):
            start_date, count = recipient_rounds[recipient]
            attributed = [
                response
                for response in account_responses
                if (letter_id := getattr(response, "dispute_letter_id", None)) is not None
                and letter_recipient.get(letter_id) == recipient
            ]
            responded = any(
                getattr(response, "outcome", None) != DisputeResponseOutcome.NO_RESPONSE
                for response in attributed
            )
            extended = document_extends_window(
                clock_start_date=start_date,
                document_dates=document_dates,
            )
            clock = compute_reinvestigation_clock(
                last_dispute_date=start_date,
                today=today,
                response_recorded=responded,
                extended=extended,
            )
            recipient_clocks.append(
                AccountReinvestigationRecipientClock(
                    recipient_type=recipient,
                    clock_start_date=start_date,
                    dispute_round_count=count,
                    deadline=clock.deadline,
                    days_remaining=clock.days_remaining,
                    state=clock.state,
                    extended=clock.extended,
                    response_count=len(attributed),
                )
            )
        return recipient_clocks

    async def _case_document_dates(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> tuple[dict[uuid.UUID, list[date]], list[date]]:
        """Per-account and case-level document upload dates for §611 extension.

        Returns ``(dates_by_account, case_level_dates)``. Case-level documents
        (no ``account_id``) apply to every tradeline; account-linked documents
        apply only to that tradeline. Used to detect the 45-day §611(a)(1)(B)
        extension signal (consumer info supplied mid-reinvestigation).
        """
        by_account: dict[uuid.UUID, list[date]] = {}
        case_level: list[date] = []
        if self._session is None:
            return by_account, case_level
        rows = await DocumentRepository(self._session).list_case_document_dates(
            organization_id=organization_id,
            case_id=case_id,
        )
        for account_id, created_at in rows:
            upload_date = created_at.date()
            if account_id is None:
                case_level.append(upload_date)
            else:
                by_account.setdefault(account_id, []).append(upload_date)
        return by_account, case_level

    @staticmethod
    def _latest_response_outcome(
        account: Account,
        responses: list[object],
    ) -> DisputeResponseRecordOutcome | None:
        """Most recent recorded response outcome, else inferred from dispute status.

        ``responses`` arrive newest-first from the repository. Falls back to the
        account's terminal ``dispute_status`` so accounts recorded via the legacy
        ``dispute-response-received`` path still yield a readiness signal.
        """
        outcome_value: str | None = None
        if responses:
            outcome = getattr(responses[0], "outcome", None)
            if outcome is not None:
                outcome_value = outcome.value if hasattr(outcome, "value") else str(outcome)
        if outcome_value is None:
            status_map = {
                DisputeStatus.VERIFIED: "verified",
                DisputeStatus.CORRECTED: "corrected",
                DisputeStatus.DELETED: "deleted",
            }
            outcome_value = status_map.get(account.dispute_status)
        return cast("DisputeResponseRecordOutcome | None", outcome_value)

    async def escalate_overdue_investigation(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> AccountResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)

        if account.investigation_status == InvestigationStatus.OVERDUE:
            updated = await self._escalate_overdue_investigation(user, account)
            return AccountResponse.from_model(updated)

        if account.dispute_status != DisputeStatus.AWAITING_RESPONSE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Account must be awaiting response before marking investigation overdue",
            )

        if account.investigation_status != InvestigationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Investigation must be pending before marking overdue",
            )

        if not self._cra_response_deadline_passed(account):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="CRA investigation window has not passed yet",
            )

        updated = await self._escalate_overdue_investigation(user, account)
        return AccountResponse.from_model(updated)

    async def create_dispute_draft_review_task(
        self,
        user: User,
        account_id: uuid.UUID,
    ) -> TaskResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        if self._tasks is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task repository is not configured",
            )

        existing = await self._tasks.find_active_by_account_source(
            organization_id=account.organization_id,
            account_id=account.id,
            source_module=DISPUTE_DRAFT_REVIEW_TASK_SOURCE,
            source_event_id=account.id,
        )
        if existing is not None:
            return TaskResponse.from_model(existing)

        task = Task(
            organization_id=account.organization_id,
            case_id=account.case_id,
            account_id=account.id,
            title=f"Review dispute draft for {account.creditor_name}",
            description=(
                "Review the rule-based CRA dispute draft, confirm supporting evidence, "
                "and prepare the next dispute action."
            ),
            priority=TaskPriority.HIGH,
            due_date=datetime.now(UTC) + timedelta(days=1),
            source_module=DISPUTE_DRAFT_REVIEW_TASK_SOURCE,
            source_event_id=account.id,
        )
        apply_audit_on_create(task, user.id)
        created = await self._tasks.create(task)
        if self._session is not None:
            await publish_platform_event(self._session, task_created_event(created, user.id))
        return TaskResponse.from_model(created)

    async def update_account(
        self,
        user: User,
        account_id: uuid.UUID,
        data: AccountUpdate,
    ) -> AccountResponse:
        self._require_write(user)
        account = await self._get_account_for_user(account_id, user)
        previous_account_status = account.account_status
        previous_payment_status = account.payment_status

        update_data = data.model_dump(exclude_unset=True)
        preserved_dispute = update_data.pop("dispute_status", None)
        preserved_action = update_data.pop("ai_recommended_next_action", None)
        for field, value in update_data.items():
            setattr(account, field, value)

        await self._apply_intelligence(account)
        if preserved_dispute is not None:
            account.dispute_status = preserved_dispute
        if preserved_action is not None:
            account.ai_recommended_next_action = preserved_action
        apply_audit_on_update(account, user.id)
        updated = await self._accounts.update(account)
        if self._session is not None:
            await publish_platform_event(self._session, account_updated_event(updated, user.id))
            status_changed = (
                "account_status" in update_data
                and updated.account_status != previous_account_status
            ) or (
                "payment_status" in update_data
                and updated.payment_status != previous_payment_status
            )
            if status_changed:
                prev = (
                    previous_account_status.value
                    if hasattr(previous_account_status, "value")
                    else str(previous_account_status)
                )
                await publish_platform_event(
                    self._session,
                    account_status_changed_event(updated, user.id, previous_status=prev),
                )
        return AccountResponse.from_model(updated)

    async def delete_account(self, user: User, account_id: uuid.UUID) -> None:
        self._require_delete(user)
        account = await self._get_account_for_user(account_id, user)
        account.soft_delete()
        apply_audit_on_update(account, user.id)
        await self._accounts.update(account)

    async def get_intelligence_summary(
        self,
        user: User,
        *,
        case_id: uuid.UUID | None = None,
    ) -> AccountIntelligenceSummary:
        organization_id = self._require_organization(user)
        if case_id is not None:
            await self._validate_case(case_id, organization_id)

        raw = await self._accounts.get_intelligence_summary(organization_id, case_id=case_id)
        next_action_queue = [
            NextActionItem(
                account_id=account.id,
                case_id=account.case_id,
                creditor_name=account.creditor_name,
                bureau=account.bureau,
                dispute_status=account.dispute_status,
                risk_score=account.risk_score,
                readiness_score=account.readiness_score,
                recommended_action=account.ai_recommended_next_action
                or recommend_next_action(account),
            )
            for account in raw["next_action_queue"]
        ]

        cross_bureau = None
        if case_id is not None:
            cross_bureau = await self._cross_bureau_intelligence_summary(organization_id, case_id)

        scoring_model: Literal["heuristic", "calibrated"] = (
            "calibrated"
            if is_feature_enabled(FeatureFlag.ENABLE_ML_SCORING)
            and is_feature_enabled(FeatureFlag.ENABLE_AI)
            else "heuristic"
        )

        return AccountIntelligenceSummary(
            total_accounts=raw["total_accounts"],
            total_balance=raw["total_balance"],
            collection_count=raw["collection_count"],
            charge_off_count=raw["charge_off_count"],
            critical_accounts=raw["critical_accounts"],
            dispute_ready_count=raw["dispute_ready_count"],
            evidence_needed_count=raw["evidence_needed_count"],
            total_past_due=raw["total_past_due"],
            accounts_by_bureau=raw["accounts_by_bureau"],
            accounts_by_type=raw["accounts_by_type"],
            accounts_by_status=raw["accounts_by_status"],
            highest_balance_accounts=[
                AccountResponse.from_model(a) for a in raw["highest_balance_accounts"]
            ],
            highest_risk_accounts=[
                AccountResponse.from_model(a) for a in raw["highest_risk_accounts"]
            ],
            next_action_queue=next_action_queue,
            scoring_model=scoring_model,
            cross_bureau=cross_bureau,
        )
