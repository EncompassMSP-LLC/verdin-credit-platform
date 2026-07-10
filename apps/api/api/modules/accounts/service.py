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
from api.modules.accounts.intelligence import apply_account_intelligence, recommend_next_action
from api.modules.accounts.intelligence_calibration import DiscrepancyScoringContext
from api.modules.accounts.intelligence_context import (
    build_discrepancy_context_map,
    compare_case_reports,
    cross_bureau_summary_payload,
    discrepancy_context_for_account,
)
from api.modules.accounts.models import Account, DisputeStatus, InvestigationStatus
from api.modules.accounts.permissions import ACCOUNT_DELETE_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountListFilters, AccountRepository
from api.modules.accounts.schemas import (
    AccountCreate,
    AccountDisputeDraftResponse,
    AccountDisputeResponseReceivedRequest,
    AccountIntelligenceSummary,
    AccountListParams,
    AccountResponse,
    AccountUpdate,
    CrossBureauIntelligenceSummary,
    DisputeLetterResponse,
    DisputeReasonSuggestionResponse,
    MissingEvidenceResponse,
    NextActionItem,
)
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.compliance.consent_gates import require_signed_consents
from api.modules.compliance.repository import ConsentRepository
from api.modules.documents.repository import DocumentRepository
from api.modules.documents.storage import DocumentStorage, get_document_storage
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
        if recipient_type == "furnisher":
            evidence_checklist = build_furnisher_evidence_checklist(account)
            template_id = FURNISHER_TEMPLATE_ID
            subject = f"Direct furnisher dispute — {account.creditor_name} tradeline"
            body = build_furnisher_dispute_body(account, case, disputed_items)
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
            body = build_dispute_body(account, case, disputed_items)
            requested_action = (
                "Investigate the disputed tradeline and delete or correct any information "
                "that cannot be verified as complete and accurate."
            )
            compliance_notes = [
                "Draft requires staff review before sending.",
                "Confirm consumer authorization and supporting evidence before submission.",
            ]

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

    async def export_case_dispute_mail_packets(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> tuple[bytes, str, str]:
        import zipfile
        from io import BytesIO

        organization_id = self._require_organization(user)
        case = await self._get_case_by_id(case_id, organization_id)
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

        buffer = BytesIO()
        packet_count = 0
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
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
                    context = build_mail_export_context(
                        account=account,
                        case=case,
                        dispute_letter=dispute_letter,
                        consumer_address_lines=consumer_address_lines,
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
                    archive.writestr(filename, content)
                    packet_count += 1

                if page >= page_result.pages:
                    break
                page += 1

        if packet_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dispute letter drafts found on this case",
            )

        short_case_id = str(case_id).split("-", 1)[0]
        return (
            buffer.getvalue(),
            f"case-mail-packets-{short_case_id}.zip",
            "application/zip",
        )

    async def export_case_dispute_report_excerpts(
        self,
        user: User,
        case_id: uuid.UUID,
    ) -> tuple[bytes, str, str]:
        import zipfile
        from io import BytesIO

        from api.modules.accounts.dispute_mail_attachments import build_account_report_excerpt

        organization_id = self._require_organization(user)
        case = await self._get_case_by_id(case_id, organization_id)
        await self._require_dispute_mail_consents(case)

        if self._dispute_letters is None or self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dispute letter repository is not configured",
            )

        buffer = BytesIO()
        excerpt_count = 0
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
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
                    archive.writestr(filename, content)
                    excerpt_count += 1

                if page >= page_result.pages:
                    break
                page += 1

        if excerpt_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dispute letter drafts found on this case",
            )

        short_case_id = str(case_id).split("-", 1)[0]
        return (
            buffer.getvalue(),
            f"case-report-excerpts-{short_case_id}.zip",
            "application/zip",
        )

    async def _build_mail_letter_export(
        self,
        *,
        account: Account,
        dispute_letter: DisputeLetter,
        export_format: DisputeMailExportFormat,
    ) -> tuple[bytes, str, str]:
        case = await self._get_case_for_account(account)
        consumer_address_lines = await self._resolve_consumer_address_lines(
            organization_id=account.organization_id,
            case_id=account.case_id,
        )
        context = build_mail_export_context(
            account=account,
            case=case,
            dispute_letter=dispute_letter,
            consumer_address_lines=consumer_address_lines,
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
