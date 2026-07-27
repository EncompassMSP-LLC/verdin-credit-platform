"""Read-only portal case progress service."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_run_repository import CreditAnalysisRunRepository
from api.modules.accounts.credit_analysis_schemas import (
    CreditAnalysisRunResponse,
    PortalCaseReadinessResponse,
)
from api.modules.accounts.credit_analysis_service import CreditAnalysisService
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.portal_readiness_export import (
    PortalReadinessExportFormat,
    build_portal_readiness_export,
)
from api.modules.client_portal.schemas import (
    PortalCaseDetailResponse,
    PortalCaseProgressResponse,
    PortalCaseSummaryResponse,
    PortalReadinessReportResponse,
)
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository


class ClientPortalCasesService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)
        self._credit_analysis = CreditAnalysisService(session)
        self._runs = CreditAnalysisRunRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ClientPortalCasesService":
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def _resolve_client_context(
        self,
        portal_user: ClientPortalUser,
    ) -> tuple[Client, list[str]]:
        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        contact_emails = await self._cases.list_contact_emails(
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
        )
        return client, contact_emails

    async def list_cases(
        self,
        portal_user: ClientPortalUser,
    ) -> PortalCaseProgressResponse:
        self._require_enabled()
        client, contact_emails = await self._resolve_client_context(portal_user)
        cases = await self._cases.list_cases_for_client(
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        return PortalCaseProgressResponse(
            items=[
                PortalCaseSummaryResponse(
                    id=case.id,
                    case_number=case.case_number,
                    title=case.title,
                    status=case.status,
                    stage=case.stage,
                    opened_at=case.opened_at,
                    closed_at=case.closed_at,
                    updated_at=case.updated_at,
                )
                for case in cases
            ]
        )

    async def get_case(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalCaseDetailResponse:
        self._require_enabled()
        client, contact_emails = await self._resolve_client_context(portal_user)
        case = await self._cases.get_case_for_client(
            case_id,
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        dispute_accounts = await self._cases.count_accounts_by_dispute_status(
            case.id,
            organization_id=portal_user.organization_id,
        )
        return PortalCaseDetailResponse(
            id=case.id,
            case_number=case.case_number,
            title=case.title,
            status=case.status,
            stage=case.stage,
            opened_at=case.opened_at,
            closed_at=case.closed_at,
            updated_at=case.updated_at,
            dispute_accounts=dispute_accounts,
            account_count=sum(dispute_accounts.values()),
        )

    async def get_case_readiness(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalCaseReadinessResponse:
        """Borrower-facing readiness from latest published run (band is source of truth)."""
        self._require_enabled()
        client, contact_emails = await self._resolve_client_context(portal_user)
        case = await self._cases.get_case_for_client(
            case_id,
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return await self._credit_analysis.get_portal_readiness(
            organization_id=portal_user.organization_id,
            case_id=case.id,
        )

    async def get_case_readiness_report(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> PortalReadinessReportResponse:
        """Published readiness report for borrower view/download (LRP-106)."""
        self._require_enabled()
        client, contact_emails = await self._resolve_client_context(portal_user)
        case = await self._cases.get_case_for_client(
            case_id,
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        run = await self._runs.get_latest_for_case(
            organization_id=portal_user.organization_id,
            case_id=case.id,
            status="published",
        )
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Readiness report not published yet",
            )
        payload = run.payload or {}
        return PortalReadinessReportResponse(
            case_id=case.id,
            credit_analysis_run_id=run.id,
            band=run.band,
            updated_at=run.published_at or run.generated_at,
            generated_at=run.generated_at,
            reports_evaluated=run.reports_evaluated,
            tradelines_evaluated=run.tradelines_evaluated,
            formula_version=run.formula_version,
            score_version=run.score_version,
            disclaimer=payload.get("disclaimer") or ADVISORY_DISCLAIMER,
            dimensions=list(payload.get("dimensions") or []),
            blockers=list(payload.get("blockers") or []),
        )

    async def export_case_readiness_report(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        *,
        export_format: PortalReadinessExportFormat,
    ) -> tuple[bytes, str, str]:
        """Band-first text/PDF export for the borrower. Never auto-transmitted."""
        self._require_enabled()
        client, contact_emails = await self._resolve_client_context(portal_user)
        case = await self._cases.get_case_for_client(
            case_id,
            organization_id=portal_user.organization_id,
            client=client,
            portal_email=portal_user.email,
            contact_emails=contact_emails,
        )
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        run = await self._runs.get_latest_for_case(
            organization_id=portal_user.organization_id,
            case_id=case.id,
            status="published",
        )
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Readiness report not published yet",
            )
        run_response = CreditAnalysisRunResponse(
            id=run.id,
            case_id=run.case_id,
            generated_at=run.generated_at,
            reports_evaluated=run.reports_evaluated,
            tradelines_evaluated=run.tradelines_evaluated,
            borrower_readiness_score=run.borrower_readiness_score,
            mortgage_readiness_score=run.mortgage_readiness_score,
            schema_version=run.schema_version,
            band=run.band,
            status=run.status,
            payload=run.payload,
            formula_version=run.formula_version,
            score_version=run.score_version,
            inputs_hash=run.inputs_hash,
            published_at=run.published_at,
        )
        return build_portal_readiness_export(run_response, export_format)
