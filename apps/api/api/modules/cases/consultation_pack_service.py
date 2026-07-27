"""Staff-gated consultation completed pack service (LRP-204)."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_run_repository import CreditAnalysisRunRepository
from api.modules.accounts.permissions import ACCOUNT_WRITE_ROLE
from api.modules.auth.models import User
from api.modules.cases.consultation_pack_compose import SCHEMA_VERSION, compose_consultation_pack
from api.modules.cases.consultation_pack_export import (
    ConsultationPackExportFormat,
    build_consultation_pack_export,
)
from api.modules.cases.consultation_pack_models import ConsultationPackRun
from api.modules.cases.consultation_pack_repository import ConsultationPackRepository
from api.modules.cases.consultation_pack_schemas import (
    ConsultationPackListResponse,
    ConsultationPackResponse,
    ConsultationPackSummary,
)
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.clients.repository import ClientRepository


class ConsultationPackService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = CaseRepository(session)
        self._clients = ClientRepository(session)
        self._runs = CreditAnalysisRunRepository(session)
        self._packs = ConsultationPackRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ConsultationPackService:
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

    def _to_summary(self, row: ConsultationPackRun) -> ConsultationPackSummary:
        return ConsultationPackSummary(
            id=row.id,
            case_id=row.case_id,
            generated_at=row.generated_at,
            status=row.status,
            schema_version=row.schema_version,
            credit_analysis_run_id=row.credit_analysis_run_id,
        )

    def _to_response(self, row: ConsultationPackRun) -> ConsultationPackResponse:
        return ConsultationPackResponse(
            **self._to_summary(row).model_dump(),
            payload=row.payload,
            disclaimer=ADVISORY_DISCLAIMER,
        )

    async def _get_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case

    async def create_pack(self, user: User, case_id: uuid.UUID) -> ConsultationPackResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        case = await self._get_case(case_id, organization_id)

        run = await self._runs.get_latest_for_case(
            organization_id=organization_id,
            case_id=case.id,
            status="published",
        )
        client_name = case.client_name
        if case.client_id is not None:
            client = await self._clients.get_by_id(case.client_id, organization_id=organization_id)
            if client is not None:
                client_name = client.display_name or client_name

        payload = compose_consultation_pack(
            case=case,
            run=run,
            client_display_name=client_name,
        )
        row = await self._packs.create(
            organization_id=organization_id,
            case_id=case.id,
            generated_by_id=user.id,
            schema_version=SCHEMA_VERSION,
            credit_analysis_run_id=run.id if run is not None else None,
            payload=payload,
        )
        await self._session.commit()
        return self._to_response(row)

    async def list_packs(self, user: User, case_id: uuid.UUID) -> ConsultationPackListResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        rows, _ = await self._packs.list_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        return ConsultationPackListResponse(items=[self._to_summary(r) for r in rows])

    async def get_latest(self, user: User, case_id: uuid.UUID) -> ConsultationPackResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        row = await self._packs.get_latest_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No consultation pack found for this case",
            )
        return self._to_response(row)

    async def get_pack(
        self, user: User, case_id: uuid.UUID, run_id: uuid.UUID
    ) -> ConsultationPackResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        row = await self._packs.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            run_id=run_id,
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation pack not found",
            )
        return self._to_response(row)

    async def export_pack(
        self,
        user: User,
        case_id: uuid.UUID,
        run_id: uuid.UUID,
        *,
        export_format: ConsultationPackExportFormat,
    ) -> tuple[bytes, str, str]:
        pack = await self.get_pack(user, case_id, run_id)
        return build_consultation_pack_export(
            pack.payload,
            case_id=str(case_id),
            export_format=export_format,
        )
