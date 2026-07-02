"""Reporting endpoints — read-optimized operational summaries."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.reporting.dependencies import get_reporting_organization_id
from api.modules.reporting.schemas import (
    BureauPerformanceReportingResponse,
    EnterpriseReportingStatusResponse,
    OperationsReportingResponse,
    TeamProductivityReportingResponse,
)
from api.modules.reporting.service import ReportingService

router = APIRouter(prefix="/reporting", tags=["Reporting"])


def get_reporting_service(db: AsyncSession = Depends(get_db)) -> ReportingService:
    return ReportingService.from_session(db)


@router.get("/operations", response_model=OperationsReportingResponse)
async def get_operations_reporting(
    organization_id: uuid.UUID = Depends(get_reporting_organization_id),
    service: ReportingService = Depends(get_reporting_service),
) -> OperationsReportingResponse:
    """Return org-scoped operations reporting read model."""
    return await service.get_operations_summary_for_organization(organization_id)


@router.get("/status", response_model=EnterpriseReportingStatusResponse)
async def get_enterprise_reporting_status(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> EnterpriseReportingStatusResponse:
    return await service.get_enterprise_status(current_user)


@router.get("/bureau-performance", response_model=BureauPerformanceReportingResponse)
async def get_bureau_performance_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> BureauPerformanceReportingResponse:
    return await service.get_bureau_performance(current_user)


@router.get("/team-productivity", response_model=TeamProductivityReportingResponse)
async def get_team_productivity_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> TeamProductivityReportingResponse:
    return await service.get_team_productivity(current_user)
