"""Service for Intelligent Letter Draft Builder (LRP-406)."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.modules.accounts.letter_draft_builder_catalog import LETTER_TEMPLATES, get_template
from api.modules.accounts.letter_draft_builder_engine import (
    TRANSMISSION_STATUSES,
    apply_section_edit,
    build_letter_draft,
    compose_full_text,
    next_workflow_status,
    validate_draft_text,
)
from api.modules.accounts.letter_draft_builder_models import (
    IntelligentLetterDraft,
    LetterDraftWorkflowStatus,
)
from api.modules.accounts.letter_draft_builder_repository import (
    LetterDraftBuilderRepository,
    snapshot_version,
)
from api.modules.accounts.letter_draft_builder_schemas import (
    LetterDraftAdvanceRequest,
    LetterDraftCreateRequest,
    LetterDraftListResponse,
    LetterDraftMarkSentRequest,
    LetterDraftResponse,
    LetterDraftSection,
    LetterDraftSectionUpdateRequest,
    LetterDraftSummary,
    LetterDraftTemplateSummary,
)
from api.modules.accounts.permissions import ACCOUNT_WRITE_ROLE
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.clients.repository import ClientRepository
from api.modules.documents.service import DocumentService


class LetterDraftBuilderService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = CaseRepository(session)
        self._clients = ClientRepository(session)
        self._drafts = LetterDraftBuilderRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> LetterDraftBuilderService:
        return cls(session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    async def _get_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case

    async def _client_name(self, case: Case, organization_id: uuid.UUID) -> str:
        name = case.client_name or "Client"
        if case.client_id is not None:
            client = await self._clients.get_by_id(case.client_id, organization_id=organization_id)
            if client is not None and client.display_name:
                name = client.display_name
        return name

    def _to_response(self, draft: IntelligentLetterDraft) -> LetterDraftResponse:
        template_title = None
        try:
            template_title = get_template(draft.template_kind).title  # type: ignore[arg-type]
        except KeyError:
            template_title = draft.template_kind
        return LetterDraftResponse(
            id=draft.id,
            organization_id=draft.organization_id,
            case_id=draft.case_id,
            created_by_user_id=draft.created_by_user_id,
            template_kind=draft.template_kind,  # type: ignore[arg-type]
            template_title=template_title,
            workflow_status=draft.workflow_status,
            issue_source_id=draft.issue_source_id,
            account_id=draft.account_id,
            version=draft.version,
            sections=[LetterDraftSection.model_validate(s) for s in (draft.sections or [])],
            full_text=draft.full_text,
            validation=dict(draft.validation or {}),
            claim_warnings=list(draft.claim_warnings or []),
            send_guardrails=dict(draft.send_guardrails or {}),
            versions_history=list(draft.versions_history or []),
            disclaimer=draft.disclaimer,
            created_at=draft.created_at,
            updated_at=draft.updated_at,
        )

    def _to_summary(self, draft: IntelligentLetterDraft) -> LetterDraftSummary:
        validation = draft.validation or {}
        return LetterDraftSummary(
            id=draft.id,
            case_id=draft.case_id,
            template_kind=draft.template_kind,  # type: ignore[arg-type]
            workflow_status=draft.workflow_status,
            issue_source_id=draft.issue_source_id,
            version=draft.version,
            validation_ok=bool(validation.get("ok", False)),
            created_at=draft.created_at,
            updated_at=draft.updated_at,
        )

    @staticmethod
    def _template_summaries() -> list[LetterDraftTemplateSummary]:
        return [
            LetterDraftTemplateSummary(
                kind=t.kind,
                title=t.title,
                description=t.description,
                claim_warnings=list(t.claim_warnings),
            )
            for t in LETTER_TEMPLATES
        ]

    async def _issue_context(
        self,
        user: User,
        case_id: uuid.UUID,
        issue_source_id: str | None,
    ) -> dict[str, Any]:
        if not issue_source_id:
            return {}
        docs = DocumentService.from_session(self._session)
        explain = await docs.get_case_issue_explainability(user, case_id)
        for card in explain.cards:
            if card.source_id == issue_source_id:
                return {
                    "issue_title": card.title,
                    "what_we_found": card.what_we_found,
                    "why_disputable": card.why_disputable,
                    "creditor_name": card.creditor_name,
                    "account_number_masked": card.account_number_masked,
                    "bureau": card.bureau,
                    "issue_source_id": card.source_id,
                    "issue_rule_id": card.rule_id,
                    "evidence_refs": [
                        {
                            "kind": "evidence_recommendation",
                            "label": item,
                        }
                        for item in (card.evidence_recommendations or [])[:5]
                    ],
                }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue source not found on this case",
        )

    async def _legal_context_for_issue(
        self,
        user: User,
        case_id: uuid.UUID,
        issue_ctx: dict[str, Any],
        template_kind: str,
    ) -> dict[str, Any]:
        """Pick strongest deletion-oriented FCRA citations when issue context exists."""
        creditor_name = issue_ctx.get("creditor_name")
        if not creditor_name:
            return {}

        from api.modules.accounts.dispute_drafts import DisputeRecipientType
        from api.modules.accounts.dispute_legal_references import (
            candidates_from_fcra_documents,
            rank_legal_alternatives,
            select_best_legal_reference,
        )

        recipient_type: DisputeRecipientType = (
            "furnisher" if template_kind == "furnisher_dispute" else "credit_bureau"
        )
        docs = DocumentService.from_session(self._session)
        try:
            fcra = await docs.get_case_fcra_findings(user, case_id)
        except HTTPException:
            return {}

        candidates = candidates_from_fcra_documents(
            fcra.documents,
            creditor_name=str(creditor_name),
            account_number_masked=issue_ctx.get("account_number_masked"),
            bureau=issue_ctx.get("bureau"),
        )
        selected = select_best_legal_reference(recipient_type, candidates)
        alternatives = rank_legal_alternatives(recipient_type, candidates)
        return {
            "legal_pursuant": selected.pursuant_clause,
            "legal_citations": list(selected.citations),
            "legal_reference_rule_id": selected.source_rule_id,
            "legal_alternatives_summary": [
                alt.rationale for alt in alternatives if not alt.selected
            ],
        }

    async def list_drafts(self, user: User, case_id: uuid.UUID) -> LetterDraftListResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        rows = await self._drafts.list_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        return LetterDraftListResponse(
            items=[self._to_summary(r) for r in rows],
            templates=self._template_summaries(),
        )

    async def get_draft(
        self, user: User, case_id: uuid.UUID, draft_id: uuid.UUID
    ) -> LetterDraftResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        draft = await self._drafts.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            draft_id=draft_id,
        )
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Letter draft not found"
            )
        return self._to_response(draft)

    async def create_draft(
        self, user: User, case_id: uuid.UUID, body: LetterDraftCreateRequest
    ) -> LetterDraftResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        case = await self._get_case(case_id, organization_id)
        client_name = await self._client_name(case, organization_id)
        issue_ctx = await self._issue_context(user, case_id, body.issue_source_id)
        legal_ctx = await self._legal_context_for_issue(
            user, case_id, issue_ctx, body.template_kind
        )

        built = build_letter_draft(
            template_kind=body.template_kind,
            client_name=client_name,
            case_id=case.id,
            **issue_ctx,
            **legal_ctx,
        )

        draft = IntelligentLetterDraft(
            organization_id=organization_id,
            case_id=case.id,
            created_by_user_id=user.id,
            template_kind=body.template_kind,
            workflow_status=LetterDraftWorkflowStatus.AI_DRAFT_CREATED,
            issue_source_id=body.issue_source_id,
            account_id=body.account_id,
            version=1,
            sections=built["sections"],
            full_text=built["full_text"],
            validation=built["validation"],
            claim_warnings=built["claim_warnings"],
            send_guardrails=built["send_guardrails"],
            versions_history=[],
            disclaimer=built["disclaimer"],
        )
        await self._drafts.add(draft)
        await self._session.commit()
        await self._session.refresh(draft)
        return self._to_response(draft)

    async def update_section(
        self,
        user: User,
        case_id: uuid.UUID,
        draft_id: uuid.UUID,
        section_key: str,
        body: LetterDraftSectionUpdateRequest,
    ) -> LetterDraftResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        draft = await self._drafts.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            draft_id=draft_id,
        )
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Letter draft not found"
            )
        if draft.workflow_status in {
            LetterDraftWorkflowStatus.SENT_RECORDED,
            LetterDraftWorkflowStatus.DELIVERY_CONFIRMED,
            LetterDraftWorkflowStatus.RESPONSE_RECEIVED,
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot edit a draft after transmission was recorded",
            )

        history = list(draft.versions_history or [])
        history.append(snapshot_version(draft))
        try:
            sections = apply_section_edit(
                list(draft.sections or []),
                section_key,
                body=body.body,
                fact_classification=body.fact_classification,
            )
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found",
            ) from None
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        full_text = compose_full_text(sections)
        validation = validate_draft_text(
            full_text,
            sections=sections,
            template_kind=draft.template_kind,  # type: ignore[arg-type]
        )
        draft.sections = sections
        draft.full_text = full_text
        draft.validation = validation
        draft.versions_history = history
        draft.version = int(draft.version) + 1
        await self._drafts.save(draft)
        await self._session.commit()
        await self._session.refresh(draft)
        return self._to_response(draft)

    async def validate_draft(
        self, user: User, case_id: uuid.UUID, draft_id: uuid.UUID
    ) -> LetterDraftResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        draft = await self._drafts.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            draft_id=draft_id,
        )
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Letter draft not found"
            )
        validation = validate_draft_text(
            draft.full_text,
            sections=list(draft.sections or []),
            template_kind=draft.template_kind,  # type: ignore[arg-type]
        )
        draft.validation = validation
        await self._drafts.save(draft)
        await self._session.commit()
        await self._session.refresh(draft)
        return self._to_response(draft)

    async def advance_workflow(
        self,
        user: User,
        case_id: uuid.UUID,
        draft_id: uuid.UUID,
        body: LetterDraftAdvanceRequest,
    ) -> LetterDraftResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        draft = await self._drafts.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            draft_id=draft_id,
        )
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Letter draft not found"
            )

        target = body.target_status.value
        if target in TRANSMISSION_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Use mark-sent to record transmission. The platform never auto-transmits letters."
                ),
            )

        current = draft.workflow_status.value
        try:
            next_status = next_workflow_status(current, target)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        if next_status in {"approved", "ready_to_send"} and not (draft.validation or {}).get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resolve blocking validation findings before approval",
            )

        draft.workflow_status = LetterDraftWorkflowStatus(next_status)
        # Guardrails always remain blocked for platform transmission.
        guardrails = dict(draft.send_guardrails or {})
        guardrails["auto_transmit"] = False
        guardrails["transmission_blocked"] = True
        draft.send_guardrails = guardrails
        await self._drafts.save(draft)
        await self._session.commit()
        await self._session.refresh(draft)
        return self._to_response(draft)

    async def mark_sent(
        self,
        user: User,
        case_id: uuid.UUID,
        draft_id: uuid.UUID,
        body: LetterDraftMarkSentRequest,
    ) -> LetterDraftResponse:
        """Record that staff transmitted the letter outside the platform. No API send."""
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        draft = await self._drafts.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            draft_id=draft_id,
        )
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Letter draft not found"
            )
        if draft.workflow_status != LetterDraftWorkflowStatus.READY_TO_SEND:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Draft must be ready_to_send before recording transmission",
            )
        if not (draft.validation or {}).get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resolve blocking validation findings before recording transmission",
            )

        history = list(draft.versions_history or [])
        history.append(snapshot_version(draft))
        if body.note:
            history[-1]["mark_sent_note"] = body.note
        draft.versions_history = history
        draft.workflow_status = LetterDraftWorkflowStatus.SENT_RECORDED
        draft.version = int(draft.version) + 1
        guardrails = dict(draft.send_guardrails or {})
        guardrails["auto_transmit"] = False
        guardrails["transmission_blocked"] = True
        guardrails["last_transmission_recorded_by_staff"] = True
        draft.send_guardrails = guardrails
        await self._drafts.save(draft)
        await self._session.commit()
        await self._session.refresh(draft)
        return self._to_response(draft)
