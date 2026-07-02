"""Reporting endpoints — read-optimized operational summaries."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.reporting.schemas import OperationsReportingResponse
from api.modules.reporting.service import ReportingService

router = APIRouter(prefix="/reporting", tags=["Reporting"])


def get_reporting_service(db: AsyncSession = Depends(get_db)) -> ReportingService:
    return ReportingService.from_session(db)


@router.get("/operations", response_model=OperationsReportingResponse)
async def get_operations_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> OperationsReportingResponse:
    """Return org-scoped operations reporting read model."""
    return await service.get_operations_summary(current_user)
