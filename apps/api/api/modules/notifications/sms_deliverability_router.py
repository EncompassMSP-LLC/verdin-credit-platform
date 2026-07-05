"""SMS deliverability dashboard scaffold endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.notifications.sms_deliverability_dependencies import (
    require_sms_deliverability_dashboard_enabled,
)
from api.modules.notifications.sms_deliverability_schemas import (
    SmsDeliverabilityDashboardStatusResponse,
    SmsDeliverabilityMetricsResponse,
)
from api.modules.notifications.sms_deliverability_service import SmsDeliverabilityDashboardService

sms_deliverability_router = APIRouter(
    prefix="/sms-campaigns/deliverability",
    tags=["SMS Deliverability"],
)


def get_sms_deliverability_dashboard_service(
    db: AsyncSession = Depends(get_db),
) -> SmsDeliverabilityDashboardService:
    return SmsDeliverabilityDashboardService.from_session(db)


@sms_deliverability_router.get("/status", response_model=SmsDeliverabilityDashboardStatusResponse)
async def get_sms_deliverability_dashboard_status_endpoint(
    _: None = Depends(require_sms_deliverability_dashboard_enabled),
    service: SmsDeliverabilityDashboardService = Depends(get_sms_deliverability_dashboard_service),
) -> SmsDeliverabilityDashboardStatusResponse:
    return service.get_status_response()


@sms_deliverability_router.get("/summary", response_model=SmsDeliverabilityMetricsResponse)
async def get_sms_deliverability_summary(
    _: None = Depends(require_sms_deliverability_dashboard_enabled),
    current_user: User = Depends(get_current_user),
    service: SmsDeliverabilityDashboardService = Depends(get_sms_deliverability_dashboard_service),
) -> SmsDeliverabilityMetricsResponse:
    return await service.get_metrics(current_user)
