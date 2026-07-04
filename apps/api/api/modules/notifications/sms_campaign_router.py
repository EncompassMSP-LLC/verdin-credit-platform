"""SMS marketing campaign scaffold endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.notifications.sms_campaign_dependencies import (
    require_sms_marketing_campaigns_enabled,
)
from api.modules.notifications.sms_campaign_schemas import (
    SmsMarketingCampaignRunListParams,
    SmsMarketingCampaignRunRequest,
    SmsMarketingCampaignRunResponse,
    SmsMarketingCampaignRunResultResponse,
    SmsMarketingCampaignStatusResponse,
)
from api.modules.notifications.sms_campaign_service import SmsMarketingCampaignService

sms_campaign_router = APIRouter(prefix="/sms-campaigns", tags=["SMS Marketing"])


def get_sms_marketing_campaign_service(
    db: AsyncSession = Depends(get_db),
) -> SmsMarketingCampaignService:
    return SmsMarketingCampaignService.from_session(db)


@sms_campaign_router.get("/status", response_model=SmsMarketingCampaignStatusResponse)
async def get_sms_marketing_campaign_status_endpoint(
    _: None = Depends(require_sms_marketing_campaigns_enabled),
    service: SmsMarketingCampaignService = Depends(get_sms_marketing_campaign_service),
) -> SmsMarketingCampaignStatusResponse:
    return service.get_status_response()


@sms_campaign_router.get(
    "/runs",
    response_model=PaginatedResponse[SmsMarketingCampaignRunResponse],
)
async def list_sms_marketing_campaign_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_sms_marketing_campaigns_enabled),
    current_user: User = Depends(get_current_user),
    service: SmsMarketingCampaignService = Depends(get_sms_marketing_campaign_service),
) -> PaginatedResponse[SmsMarketingCampaignRunResponse]:
    params = SmsMarketingCampaignRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@sms_campaign_router.post(
    "/run",
    response_model=SmsMarketingCampaignRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def enqueue_sms_marketing_campaign_endpoint(
    body: SmsMarketingCampaignRunRequest,
    _: None = Depends(require_sms_marketing_campaigns_enabled),
    current_user: User = Depends(get_current_user),
    service: SmsMarketingCampaignService = Depends(get_sms_marketing_campaign_service),
) -> SmsMarketingCampaignRunResultResponse:
    return await service.enqueue_campaign(current_user, body)
