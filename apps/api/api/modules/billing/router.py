"""Organization billing endpoints."""

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.collection_schemas import (
    BillingInvoiceCollectionRunListParams,
    BillingInvoiceCollectionRunRequest,
    BillingInvoiceCollectionRunResponse,
    BillingInvoiceCollectionRunResultResponse,
    BillingInvoiceCollectionStatusResponse,
)
from api.modules.billing.dependencies import (
    require_billing_enabled,
    require_billing_invoice_collection_enabled,
    require_billing_invoicing_enabled,
    require_usage_metering_enabled,
)
from api.modules.billing.invoicing_schemas import (
    BillingInvoicingRunListParams,
    BillingInvoicingRunRequest,
    BillingInvoicingRunResponse,
    BillingInvoicingRunResultResponse,
    BillingInvoicingStatusResponse,
)
from api.modules.billing.schemas import (
    BillingSetupResponse,
    BillingStatusResponse,
    BillingSubscribeRequest,
    BillingSubscribeResponse,
    BillingUsageRecordRequest,
    BillingUsageRecordResponse,
    BillingUsageSummaryResponse,
    StripeWebhookResponse,
)
from api.modules.billing.service import BillingService
from api.modules.org_admin.dependencies import require_org_admin_enabled

router = APIRouter(prefix="/billing", tags=["Billing"])


def get_billing_service(db: AsyncSession = Depends(get_db)) -> BillingService:
    return BillingService.from_session(db)


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status_endpoint(
    _: None = Depends(require_billing_enabled),
    _current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingStatusResponse:
    return service.get_billing_status_response()


@router.post("/setup", response_model=BillingSetupResponse, status_code=status.HTTP_201_CREATED)
async def setup_organization_billing(
    _: None = Depends(require_billing_enabled),
    __: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingSetupResponse:
    return await service.setup_billing(current_user)


@router.post("/subscribe", response_model=BillingSubscribeResponse)
async def subscribe_organization_billing(
    body: BillingSubscribeRequest,
    _: None = Depends(require_billing_enabled),
    __: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingSubscribeResponse:
    return await service.subscribe(current_user, body)


@router.post("/webhooks/stripe", response_model=StripeWebhookResponse)
async def stripe_billing_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    service: BillingService = Depends(get_billing_service),
) -> StripeWebhookResponse:
    payload = await request.body()
    return await service.handle_stripe_webhook(payload, stripe_signature)


@router.get("/usage/summary", response_model=BillingUsageSummaryResponse)
async def get_billing_usage_summary(
    _: None = Depends(require_usage_metering_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingUsageSummaryResponse:
    return await service.get_usage_summary(current_user)


@router.post(
    "/usage/events",
    response_model=BillingUsageRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_billing_usage_event(
    body: BillingUsageRecordRequest,
    _: None = Depends(require_usage_metering_enabled),
    __: None = Depends(require_org_admin_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingUsageRecordResponse:
    return await service.record_usage_event(current_user, body)


@router.get("/invoicing/status", response_model=BillingInvoicingStatusResponse)
async def get_billing_invoicing_status_endpoint(
    _: None = Depends(require_billing_invoicing_enabled),
    service: BillingService = Depends(get_billing_service),
) -> BillingInvoicingStatusResponse:
    return service.get_invoicing_status_response()


@router.get(
    "/invoicing/runs",
    response_model=PaginatedResponse[BillingInvoicingRunResponse],
)
async def list_billing_invoicing_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_billing_invoicing_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> PaginatedResponse[BillingInvoicingRunResponse]:
    params = BillingInvoicingRunListParams(page=page, page_size=page_size)
    return await service.list_invoicing_runs(current_user, params)


@router.post("/invoicing/run", response_model=BillingInvoicingRunResultResponse)
async def run_billing_invoicing_endpoint(
    body: BillingInvoicingRunRequest,
    _: None = Depends(require_billing_invoicing_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingInvoicingRunResultResponse:
    return await service.run_invoicing_cycle(current_user, body)


@router.get("/collection/status", response_model=BillingInvoiceCollectionStatusResponse)
async def get_billing_invoice_collection_status_endpoint(
    _: None = Depends(require_billing_invoice_collection_enabled),
    service: BillingService = Depends(get_billing_service),
) -> BillingInvoiceCollectionStatusResponse:
    return service.get_collection_status_response()


@router.get(
    "/collection/runs",
    response_model=PaginatedResponse[BillingInvoiceCollectionRunResponse],
)
async def list_billing_invoice_collection_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_billing_invoice_collection_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> PaginatedResponse[BillingInvoiceCollectionRunResponse]:
    params = BillingInvoiceCollectionRunListParams(page=page, page_size=page_size)
    return await service.list_collection_runs(current_user, params)


@router.post("/collection/run", response_model=BillingInvoiceCollectionRunResultResponse)
async def run_billing_invoice_collection_endpoint(
    body: BillingInvoiceCollectionRunRequest,
    _: None = Depends(require_billing_invoice_collection_enabled),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> BillingInvoiceCollectionRunResultResponse:
    return await service.run_collection_cycle(current_user, body)
