"""Compliance center service — consent records and retention policy placeholders."""

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.compliance import get_compliance_center_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import Organization, User
from api.modules.cases.repository import CaseRepository
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository
from api.modules.compliance.consent_gates import get_missing_signed_template_keys
from api.modules.compliance.consent_signature import is_consent_signed
from api.modules.compliance.consent_template_service import ConsentTemplateService
from api.modules.compliance.consent_templates.defaults import DEFAULT_TEMPLATE_BY_KEY
from api.modules.compliance.consent_templates.keys import (
    DISPUTE_MAIL_REQUIRED_TEMPLATES,
    LEGAL_REVIEW_NOTICE,
    TEMPLATE_CONSENT_TYPE,
    TEMPLATE_LABELS,
    ConsentDocumentTemplateKey,
)
from api.modules.compliance.enforcement import enforce_retention_policies_for_organization
from api.modules.compliance.enforcement_repository import (
    EnforcementRunListFilters,
    RetentionEnforcementRunRepository,
)
from api.modules.compliance.models import (
    ConsentRecord,
    ConsentSignatureMethod,
    ConsentStatus,
    ConsentType,
    EnforcementTriggerSource,
    RetentionPolicy,
)
from api.modules.compliance.permissions import (
    COMPLIANCE_ADMIN_ROLE,
    COMPLIANCE_READ_ROLE,
    COMPLIANCE_WRITE_ROLE,
)
from api.modules.compliance.repository import (
    ConsentListFilters,
    ConsentRepository,
    RetentionPolicyListFilters,
    RetentionPolicyRepository,
)
from api.modules.compliance.schemas import (
    ClientConsentGapsResponse,
    ComplianceCenterStatusResponse,
    ConsentDocumentTemplateResponse,
    ConsentDocumentTemplateUpdate,
    ConsentRecordCreate,
    ConsentRecordListParams,
    ConsentRecordResponse,
    PortalCaseConsentsResponse,
    PortalConsentRequirementResponse,
    RetentionEnforcementRunListParams,
    RetentionEnforcementRunResponse,
    RetentionEnforcementRunResultResponse,
    RetentionEnforcementStatusResponse,
    RetentionPolicyCreate,
    RetentionPolicyListParams,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
)
from api.modules.documents.service import DocumentService
from api.modules.documents.storage import DocumentStorage, get_document_storage

PORTAL_CONSENT_ATTESTATIONS: dict[ConsentDocumentTemplateKey, str] = {
    ConsentDocumentTemplateKey.CROA_DISCLOSURE: (
        "I have read the Credit Repair Organizations Act disclosure statement above and "
        "acknowledge my right to cancel within three business days."
    ),
    ConsentDocumentTemplateKey.CROA_SERVICE_AGREEMENT: (
        "I have read and agree to the credit repair services agreement, including fees, "
        "services, and cancellation terms."
    ),
    ConsentDocumentTemplateKey.FCRA_AUTHORIZATION: (
        "I authorize the organization to obtain and dispute information in my consumer "
        "credit reports on my behalf under the Fair Credit Reporting Act."
    ),
}


class ComplianceService:
    def __init__(
        self,
        consent_repo: ConsentRepository,
        retention_repo: RetentionPolicyRepository,
        client_repo: ClientRepository,
        case_repo: CaseRepository,
        enforcement_run_repo: RetentionEnforcementRunRepository | None = None,
        document_service: DocumentService | None = None,
        template_service: ConsentTemplateService | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self._consents = consent_repo
        self._retention = retention_repo
        self._clients = client_repo
        self._cases = case_repo
        self._enforcement_runs = enforcement_run_repo
        self._documents = document_service
        self._templates = template_service
        self._session = session

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        storage: DocumentStorage | None = None,
    ) -> "ComplianceService":
        document_storage = storage or get_document_storage()
        return cls(
            ConsentRepository(session),
            RetentionPolicyRepository(session),
            ClientRepository(session),
            CaseRepository(session),
            RetentionEnforcementRunRepository(session),
            DocumentService.from_session(session, document_storage),
            ConsentTemplateService.from_session(session),
            session=session,
        )

    async def _get_organization(self, organization_id: uuid.UUID) -> Organization:
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )
        organization = await self._session.get(Organization, organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return organization

    async def _get_client(self, client_id: uuid.UUID, organization_id: uuid.UUID) -> Client:
        client = await self._clients.get_by_id(client_id, organization_id=organization_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, COMPLIANCE_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view compliance records",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, COMPLIANCE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify compliance records",
            )

    def _require_admin(self, user: User) -> None:
        if not has_permission(user.role, COMPLIANCE_ADMIN_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage retention policies",
            )

    async def _ensure_client(self, client_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        client = await self._clients.get_by_id(client_id, organization_id=organization_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

    async def _ensure_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        *,
        client_id: uuid.UUID | None = None,
    ) -> None:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        if client_id is not None and case.client_id is not None and case.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case is not linked to the specified client",
            )

    async def get_status(self, user: User) -> ComplianceCenterStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        return get_compliance_center_status()

    async def list_consents(
        self,
        user: User,
        params: ConsentRecordListParams,
    ) -> PaginatedResponse[ConsentRecordResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        records, total = await self._consents.list_consents(
            ConsentListFilters(
                organization_id=organization_id,
                client_id=params.client_id,
                case_id=params.case_id,
                consent_type=params.consent_type,
                status=params.status,
                skip=skip,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        items = [ConsentRecordResponse.from_model(record) for record in records]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def get_consent(self, user: User, consent_id: uuid.UUID) -> ConsentRecordResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        record = await self._consents.get_by_id(consent_id, organization_id=organization_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent record not found",
            )
        return ConsentRecordResponse.from_model(record)

    async def create_consent(self, user: User, data: ConsentRecordCreate) -> ConsentRecordResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._ensure_client(data.client_id, organization_id)
        if data.case_id is not None:
            await self._ensure_case(data.case_id, organization_id, client_id=data.client_id)

        granted_at = data.granted_at or datetime.now(UTC)
        record = ConsentRecord(
            organization_id=organization_id,
            client_id=data.client_id,
            case_id=data.case_id,
            consent_type=data.consent_type,
            status=ConsentStatus.GRANTED,
            granted_at=granted_at,
            source=data.source,
            notes=data.notes,
        )
        apply_audit_on_create(record, user.id)
        record = await self._consents.create(record)
        if self._session is not None:
            await self._session.commit()
        return ConsentRecordResponse.from_model(record)

    async def upload_signed_consent(
        self,
        user: User,
        *,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
        consent_type: ConsentType,
        file: UploadFile,
        signer_name: str | None = None,
        notes: str | None = None,
        document_template_key: str | None = None,
    ) -> ConsentRecordResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._ensure_client(client_id, organization_id)
        await self._ensure_case(case_id, organization_id, client_id=client_id)
        if self._documents is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document service is not configured",
            )

        document = await self._documents.upload_signed_consent_document(
            user,
            case_id=case_id,
            file=file,
            consent_type=consent_type.value,
            client_id=client_id,
        )
        now = datetime.now(UTC)
        record = ConsentRecord(
            organization_id=organization_id,
            client_id=client_id,
            case_id=case_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED,
            granted_at=now,
            source="staff_upload",
            notes=notes,
            document_id=document.id,
            signature_method=ConsentSignatureMethod.STAFF_UPLOAD.value,
            signed_at=now,
            signer_name=signer_name,
            document_template_key=document_template_key,
        )
        apply_audit_on_create(record, user.id)
        record = await self._consents.create(record)
        if self._session is not None:
            await self._session.commit()
        return ConsentRecordResponse.from_model(record)

    async def list_portal_case_consents(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> PortalCaseConsentsResponse:
        if self._templates is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Consent template service is not configured",
            )

        organization = await self._get_organization(organization_id)
        client = await self._get_client(client_id, organization_id)

        records, _ = await self._consents.list_consents(
            ConsentListFilters(
                organization_id=organization_id,
                client_id=client_id,
                case_id=case_id,
                status=ConsentStatus.GRANTED,
                skip=0,
                limit=200,
            )
        )
        signed_by_key: dict[str, ConsentRecord] = {}
        for record in records:
            if record.document_template_key and is_consent_signed(record):
                signed_by_key[record.document_template_key] = record

        items: list[PortalConsentRequirementResponse] = []
        for template_key in DISPUTE_MAIL_REQUIRED_TEMPLATES:
            resolved = await self._templates.resolve_template(
                organization_id=organization_id,
                template_key=template_key,
                organization=organization,
                client=client,
            )
            consent_type = TEMPLATE_CONSENT_TYPE[template_key]
            items.append(
                PortalConsentRequirementResponse(
                    template_key=template_key,
                    consent_type=consent_type,
                    label=TEMPLATE_LABELS[template_key],
                    title=resolved.title,
                    is_signed=template_key.value in signed_by_key,
                    consent_id=signed_by_key[template_key.value].id
                    if template_key.value in signed_by_key
                    else None,
                    legal_review_status=resolved.legal_review_status,
                )
            )
        return PortalCaseConsentsResponse(items=items, legal_review_notice=LEGAL_REVIEW_NOTICE)

    async def preview_portal_consent_document(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        template_key: ConsentDocumentTemplateKey,
    ) -> tuple[bytes, str]:
        if self._templates is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Consent template service is not configured",
            )
        organization = await self._get_organization(organization_id)
        client = await self._get_client(client_id, organization_id)
        resolved = await self._templates.resolve_template(
            organization_id=organization_id,
            template_key=template_key,
            organization=organization,
            client=client,
        )
        pdf_bytes = self._templates.render_preview_pdf(resolved)
        filename = f"consent-preview-{template_key.value}.pdf"
        return pdf_bytes, filename

    async def sign_portal_consent(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
        portal_user_id: uuid.UUID,
        template_key: ConsentDocumentTemplateKey,
        signer_name: str,
        attestation_accepted: bool,
        signature_file: UploadFile | None = None,
        signature_metadata: dict[str, Any] | None = None,
    ) -> ConsentRecordResponse:
        if not attestation_accepted:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Attestation must be accepted before signing consent",
            )
        if self._documents is None or self._templates is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document service is not configured",
            )

        organization = await self._get_organization(organization_id)
        client = await self._get_client(client_id, organization_id)
        resolved = await self._templates.resolve_template(
            organization_id=organization_id,
            template_key=template_key,
            organization=organization,
            client=client,
        )
        now = datetime.now(UTC)
        pdf_bytes = self._templates.render_signed_pdf(
            resolved,
            signer_name=signer_name.strip(),
            signed_at=now,
        )
        document = await self._documents.store_generated_consent_pdf(
            organization_id=organization_id,
            case_id=case_id,
            created_by_id=portal_user_id,
            title=f"Signed — {resolved.title}",
            pdf_bytes=pdf_bytes,
            template_key=template_key.value,
        )

        metadata = dict(signature_metadata or {})
        metadata["attestation_text"] = PORTAL_CONSENT_ATTESTATIONS.get(template_key, "")
        metadata["template_key"] = template_key.value
        metadata["template_title"] = resolved.title
        metadata["legal_review_status"] = resolved.legal_review_status
        if signature_file is not None and signature_file.filename:
            metadata["has_signature_image"] = True

        consent_type = TEMPLATE_CONSENT_TYPE[template_key]
        record = ConsentRecord(
            organization_id=organization_id,
            client_id=client_id,
            case_id=case_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED,
            granted_at=now,
            source="portal",
            notes=None,
            document_id=document.id,
            signature_method=ConsentSignatureMethod.PORTAL_GENERATED_DOCUMENT.value,
            signed_at=now,
            signer_name=signer_name.strip(),
            signature_metadata=metadata,
            document_template_key=template_key.value,
        )
        record = await self._consents.create(record)
        if self._session is not None:
            await self._session.commit()
        return ConsentRecordResponse.from_model(record)

    async def get_client_consent_gaps(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientConsentGapsResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        await self._ensure_client(client_id, organization_id)
        missing = await get_missing_signed_template_keys(
            self._consents,
            organization_id=organization_id,
            client_id=client_id,
        )
        return ClientConsentGapsResponse(
            missing_template_keys=[key.value for key in missing],
            missing_template_labels=[TEMPLATE_LABELS[key] for key in missing],
            missing_consent_types=await self._legacy_missing_consent_types(
                organization_id,
                client_id,
            ),
        )

    async def _legacy_missing_consent_types(
        self,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> list[str]:
        from api.modules.compliance.consent_gates import get_missing_signed_consents

        missing = await get_missing_signed_consents(
            self._consents,
            organization_id=organization_id,
            client_id=client_id,
        )
        return [consent_type.value for consent_type in missing]

    async def list_consent_templates(self, user: User) -> list[ConsentDocumentTemplateResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._templates is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Consent template service is not configured",
            )

        stored_rows = {
            row.template_key: row
            for row in await self._templates.list_org_templates(organization_id=organization_id)
        }
        items: list[ConsentDocumentTemplateResponse] = []
        for template_key in ConsentDocumentTemplateKey:
            default = DEFAULT_TEMPLATE_BY_KEY[template_key]
            stored = stored_rows.get(template_key.value)
            items.append(
                ConsentDocumentTemplateResponse(
                    template_key=template_key,
                    title=stored.title if stored else default.title,
                    body_text=stored.body_text if stored else default.body_text,
                    merge_field_defaults=stored.merge_field_defaults if stored else None,
                    legal_review_status=(stored.legal_review_status if stored else "draft"),
                    is_customized=stored is not None,
                    updated_at=stored.updated_at if stored else None,
                )
            )
        return items

    async def update_consent_template(
        self,
        user: User,
        template_key: ConsentDocumentTemplateKey,
        data: ConsentDocumentTemplateUpdate,
    ) -> ConsentDocumentTemplateResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        if self._templates is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Consent template service is not configured",
            )

        stored = await self._templates.upsert_org_template(
            organization_id=organization_id,
            template_key=template_key,
            title=data.title,
            body_text=data.body_text,
            merge_field_defaults=data.merge_field_defaults,
            legal_review_status=data.legal_review_status,
            user_id=user.id,
        )
        if self._session is not None:
            await self._session.commit()
        return ConsentDocumentTemplateResponse(
            template_key=template_key,
            title=stored.title,
            body_text=stored.body_text,
            merge_field_defaults=stored.merge_field_defaults,
            legal_review_status=stored.legal_review_status,
            is_customized=True,
            updated_at=stored.updated_at,
        )

    async def preview_consent_template_pdf(
        self,
        user: User,
        *,
        template_key: ConsentDocumentTemplateKey,
        client_id: uuid.UUID,
    ) -> tuple[bytes, str]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._templates is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Consent template service is not configured",
            )
        organization = await self._get_organization(organization_id)
        client = await self._get_client(client_id, organization_id)
        resolved = await self._templates.resolve_template(
            organization_id=organization_id,
            template_key=template_key,
            organization=organization,
            client=client,
        )
        pdf_bytes = self._templates.render_preview_pdf(resolved)
        return pdf_bytes, f"consent-preview-{template_key.value}.pdf"

    async def withdraw_consent(self, user: User, consent_id: uuid.UUID) -> ConsentRecordResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        record = await self._consents.get_by_id(consent_id, organization_id=organization_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent record not found",
            )
        if record.status == ConsentStatus.WITHDRAWN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consent has already been withdrawn",
            )

        record.status = ConsentStatus.WITHDRAWN
        record.withdrawn_at = datetime.now(UTC)
        apply_audit_on_update(record, user.id)
        record = await self._consents.save(record)
        if self._session is not None:
            await self._session.commit()
        return ConsentRecordResponse.from_model(record)

    async def list_retention_policies(
        self,
        user: User,
        params: RetentionPolicyListParams,
    ) -> PaginatedResponse[RetentionPolicyResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        policies, total = await self._retention.list_policies(
            RetentionPolicyListFilters(
                organization_id=organization_id,
                scope=params.scope,
                is_active=params.is_active,
                skip=skip,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        items = [RetentionPolicyResponse.from_model(policy) for policy in policies]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def get_retention_policy(
        self,
        user: User,
        policy_id: uuid.UUID,
    ) -> RetentionPolicyResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        policy = await self._retention.get_by_id(policy_id, organization_id=organization_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retention policy not found",
            )
        return RetentionPolicyResponse.from_model(policy)

    async def create_retention_policy(
        self,
        user: User,
        data: RetentionPolicyCreate,
    ) -> RetentionPolicyResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        policy = RetentionPolicy(
            organization_id=organization_id,
            name=data.name,
            scope=data.scope,
            retention_days=data.retention_days,
            is_active=data.is_active,
            description=data.description,
        )
        apply_audit_on_create(policy, user.id)
        policy = await self._retention.create(policy)
        if self._session is not None:
            await self._session.commit()
        return RetentionPolicyResponse.from_model(policy)

    async def update_retention_policy(
        self,
        user: User,
        policy_id: uuid.UUID,
        data: RetentionPolicyUpdate,
    ) -> RetentionPolicyResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        policy = await self._retention.get_by_id(policy_id, organization_id=organization_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retention policy not found",
            )

        if data.name is not None:
            policy.name = data.name
        if data.retention_days is not None:
            policy.retention_days = data.retention_days
        if data.is_active is not None:
            policy.is_active = data.is_active
        if data.description is not None:
            policy.description = data.description

        apply_audit_on_update(policy, user.id)
        policy = await self._retention.save(policy)
        if self._session is not None:
            await self._session.commit()
        return RetentionPolicyResponse.from_model(policy)

    async def get_enforcement_status(self, user: User) -> RetentionEnforcementStatusResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._enforcement_runs is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Enforcement repository is not configured",
            )
        active_policy_count = await self._enforcement_runs.count_active_policies(
            organization_id=organization_id,
        )
        last_run_at = await self._enforcement_runs.get_latest_started_at(
            organization_id=organization_id,
        )
        return RetentionEnforcementStatusResponse(
            enabled=is_feature_enabled(FeatureFlag.ENABLE_COMPLIANCE_ENFORCEMENT),
            active_policy_count=active_policy_count,
            last_run_at=last_run_at,
        )

    async def list_enforcement_runs(
        self,
        user: User,
        params: RetentionEnforcementRunListParams,
    ) -> PaginatedResponse[RetentionEnforcementRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._enforcement_runs is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Enforcement repository is not configured",
            )
        skip = (params.page - 1) * params.page_size
        runs, total = await self._enforcement_runs.list_runs(
            EnforcementRunListFilters(
                organization_id=organization_id,
                skip=skip,
                limit=params.page_size,
            )
        )
        items = [RetentionEnforcementRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def run_enforcement(self, user: User) -> RetentionEnforcementRunResultResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )
        summary = await enforce_retention_policies_for_organization(
            self._session,
            organization_id=organization_id,
            trigger_source=EnforcementTriggerSource.MANUAL,
            retention_repo=self._retention,
            run_repo=self._enforcement_runs,
        )
        await self._session.commit()
        return RetentionEnforcementRunResultResponse(
            policies_processed=summary.policies_processed,
            items_enforced=summary.items_enforced,
            runs=[RetentionEnforcementRunResponse.from_model(run) for run in summary.runs],
        )
