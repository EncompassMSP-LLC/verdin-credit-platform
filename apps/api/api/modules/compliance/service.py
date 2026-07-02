"""Compliance center service — consent records and retention policy placeholders."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.compliance import get_compliance_center_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.clients.repository import ClientRepository
from api.modules.compliance.models import ConsentRecord, ConsentStatus, RetentionPolicy
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
    ComplianceCenterStatusResponse,
    ConsentRecordCreate,
    ConsentRecordListParams,
    ConsentRecordResponse,
    RetentionPolicyCreate,
    RetentionPolicyListParams,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
)


class ComplianceService:
    def __init__(
        self,
        consent_repo: ConsentRepository,
        retention_repo: RetentionPolicyRepository,
        client_repo: ClientRepository,
        case_repo: CaseRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._consents = consent_repo
        self._retention = retention_repo
        self._clients = client_repo
        self._cases = case_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ComplianceService":
        return cls(
            ConsentRepository(session),
            RetentionPolicyRepository(session),
            ClientRepository(session),
            CaseRepository(session),
            session=session,
        )

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
