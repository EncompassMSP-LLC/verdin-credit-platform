"""Organization billing service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.billing_invoicing import get_billing_invoicing_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.stripe_billing import (
    BillingNotReadyError,
    create_stripe_customer,
    create_stripe_subscription,
    get_billing_status,
    get_stripe_billing_settings,
    parse_stripe_event,
    require_billing_ready,
    verify_stripe_webhook_signature,
)
from api.core.usage_metering import build_usage_summary
from api.modules.auth.models import User
from api.modules.billing.invoicing_models import BillingInvoicingRunStatus
from api.modules.billing.invoicing_processor import run_billing_invoicing_cycle
from api.modules.billing.invoicing_repository import (
    BillingInvoicingRunListFilters,
    BillingInvoicingRunRepository,
)
from api.modules.billing.invoicing_schemas import (
    BillingInvoicingRunListParams,
    BillingInvoicingRunRequest,
    BillingInvoicingRunResponse,
    BillingInvoicingRunResultResponse,
    BillingInvoicingStatusResponse,
)
from api.modules.billing.models import (
    BillingUsageEvent,
    BillingWebhookEvent,
    BillingWebhookEventStatus,
    OrganizationBillingAccount,
    SubscriptionStatus,
)
from api.modules.billing.repository import BillingRepository
from api.modules.billing.schemas import (
    BillingSetupResponse,
    BillingStatusResponse,
    BillingSubscribeRequest,
    BillingSubscribeResponse,
    BillingUsageMetricTotal,
    BillingUsageRecordRequest,
    BillingUsageRecordResponse,
    BillingUsageSummaryResponse,
    OrganizationBillingSummary,
    StripeWebhookResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class BillingService:
    def __init__(self, repo: BillingRepository, session: AsyncSession | None = None) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> BillingService:
        return cls(BillingRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view billing",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage billing",
            )

    def get_billing_status_response(self) -> BillingStatusResponse:
        billing_status = get_billing_status()
        return BillingStatusResponse(
            enabled=billing_status.enabled,
            ready=billing_status.ready,
            provider=billing_status.provider,
            default_price_id=billing_status.default_price_id,
            blockers=billing_status.blockers,
        )

    async def get_organization_billing_summary(
        self,
        organization_id: uuid.UUID,
    ) -> OrganizationBillingSummary:
        billing_status = get_billing_status()
        account = await self._repo.get_billing_account(organization_id)
        return OrganizationBillingSummary.from_account(
            enabled=billing_status.enabled,
            ready=billing_status.ready,
            account=account,
        )

    async def setup_billing(self, user: User) -> BillingSetupResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        try:
            require_billing_ready()
        except BillingNotReadyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Stripe billing is not ready", "blockers": exc.blockers},
            ) from exc

        existing = await self._repo.get_billing_account(organization_id)
        if existing is not None:
            return BillingSetupResponse(
                organization_id=organization_id,
                stripe_customer_id=existing.stripe_customer_id,
                created=False,
            )

        try:
            customer = await create_stripe_customer(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip(),
                organization_id=str(organization_id),
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        account = OrganizationBillingAccount(
            organization_id=organization_id,
            stripe_customer_id=customer.customer_id,
            subscription_status=SubscriptionStatus.NONE,
        )
        await self._repo.save_billing_account(account)
        if self._session is not None:
            await self._session.commit()

        return BillingSetupResponse(
            organization_id=organization_id,
            stripe_customer_id=customer.customer_id,
            created=True,
        )

    async def subscribe(
        self, user: User, body: BillingSubscribeRequest
    ) -> BillingSubscribeResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        try:
            billing_status = require_billing_ready()
        except BillingNotReadyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Stripe billing is not ready", "blockers": exc.blockers},
            ) from exc

        price_id = body.price_id or billing_status.default_price_id
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="price_id is required when STRIPE_DEFAULT_PRICE_ID is not configured",
            )

        account = await self._repo.get_billing_account(organization_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Billing customer not set up for organization",
            )
        if account.stripe_subscription_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization already has an active subscription record",
            )

        try:
            subscription = await create_stripe_subscription(
                customer_id=account.stripe_customer_id,
                price_id=price_id,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        account.stripe_subscription_id = subscription.subscription_id
        account.subscription_status = SubscriptionStatus(subscription.status)
        account.price_id = subscription.price_id or price_id
        account.current_period_end = (
            datetime.fromtimestamp(subscription.current_period_end, tz=UTC)
            if subscription.current_period_end is not None
            else None
        )
        await self._repo.save_billing_account(account)
        if self._session is not None:
            await self._session.commit()

        return BillingSubscribeResponse(
            organization_id=organization_id,
            stripe_customer_id=account.stripe_customer_id,
            stripe_subscription_id=account.stripe_subscription_id,
            subscription_status=account.subscription_status,
            price_id=account.price_id,
            current_period_end=account.current_period_end,
        )

    async def handle_stripe_webhook(
        self,
        payload: bytes,
        signature_header: str | None,
    ) -> StripeWebhookResponse:
        settings = get_stripe_billing_settings()
        if not settings.stripe_webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe webhook secret is not configured",
            )
        if signature_header is None or not verify_stripe_webhook_signature(
            payload,
            signature_header,
            secret=settings.stripe_webhook_secret,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Stripe webhook signature",
            )

        event = parse_stripe_event(payload)
        event_id = str(event.get("id", ""))
        event_type = str(event.get("type", ""))
        if not event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stripe event id missing",
            )

        existing = await self._repo.get_webhook_event(event_id)
        if existing is not None:
            return StripeWebhookResponse(
                received=True,
                event_id=event_id,
                status=existing.status.value,
            )

        organization_id, status_value, error_message = await self._apply_stripe_event(event)
        webhook_event = BillingWebhookEvent(
            stripe_event_id=event_id,
            event_type=event_type,
            organization_id=organization_id,
            status=status_value,
            payload=payload.decode(),
            error_message=error_message,
            processed_at=self._repo.utcnow(),
        )
        await self._repo.create_webhook_event(webhook_event)
        if self._session is not None:
            await self._session.commit()

        return StripeWebhookResponse(
            received=True,
            event_id=event_id,
            status=status_value.value,
        )

    async def _apply_stripe_event(
        self,
        event: dict[str, Any],
    ) -> tuple[uuid.UUID | None, BillingWebhookEventStatus, str | None]:
        event_type = str(event.get("type", ""))
        data_object = event.get("data", {}).get("object", {})
        if not isinstance(data_object, dict):
            return None, BillingWebhookEventStatus.IGNORED, None

        if event_type.startswith("customer.subscription."):
            return await self._sync_subscription_object(data_object)

        return None, BillingWebhookEventStatus.IGNORED, None

    async def _sync_subscription_object(
        self,
        subscription: dict[str, Any],
    ) -> tuple[uuid.UUID | None, BillingWebhookEventStatus, str | None]:
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        if not customer_id or not subscription_id:
            return None, BillingWebhookEventStatus.IGNORED, None

        account = await self._repo.get_billing_account_by_customer_id(str(customer_id))
        if account is None:
            return None, BillingWebhookEventStatus.IGNORED, None

        status_value = str(subscription.get("status", SubscriptionStatus.NONE.value))
        try:
            account.subscription_status = SubscriptionStatus(status_value)
        except ValueError:
            account.subscription_status = SubscriptionStatus.NONE

        account.stripe_subscription_id = str(subscription_id)
        items = subscription.get("items", {}).get("data", [])
        if items:
            price = items[0].get("price", {})
            if isinstance(price, dict) and price.get("id"):
                account.price_id = str(price["id"])

        period_end = subscription.get("current_period_end")
        account.current_period_end = (
            datetime.fromtimestamp(int(period_end), tz=UTC) if period_end is not None else None
        )
        await self._repo.save_billing_account(account)
        return account.organization_id, BillingWebhookEventStatus.PROCESSED, None

    async def record_usage_event(
        self,
        user: User,
        body: BillingUsageRecordRequest,
    ) -> BillingUsageRecordResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        recorded_at = self._repo.utcnow()
        event = BillingUsageEvent(
            organization_id=organization_id,
            metric_name=body.metric_name,
            quantity=body.quantity,
            source=body.source,
            recorded_at=recorded_at,
            created_by_id=user.id,
        )
        saved = await self._repo.create_usage_event(event)
        if self._session is not None:
            await self._session.commit()
        return BillingUsageRecordResponse(
            id=saved.id,
            organization_id=saved.organization_id,
            metric_name=saved.metric_name,
            quantity=saved.quantity,
            source=saved.source,
            recorded_at=saved.recorded_at,
        )

    async def get_usage_summary(self, user: User) -> BillingUsageSummaryResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        account = await self._repo.get_billing_account(organization_id)
        (
            total_events,
            metrics,
            first_recorded_at,
            last_recorded_at,
        ) = await self._repo.aggregate_usage_by_metric(organization_id)
        payload = build_usage_summary(
            organization_id=str(organization_id),
            metering_enabled=True,
            stripe_customer_configured=account is not None,
            total_events=total_events,
            metrics=metrics,
            first_recorded_at=first_recorded_at,
            last_recorded_at=last_recorded_at,
        )
        return BillingUsageSummaryResponse(
            organization_id=organization_id,
            metering_enabled=payload["metering_enabled"],
            stripe_customer_configured=payload["stripe_customer_configured"],
            total_events=payload["total_events"],
            metrics=[BillingUsageMetricTotal(**metric) for metric in payload["metrics"]],
            first_recorded_at=payload["first_recorded_at"],
            last_recorded_at=payload["last_recorded_at"],
        )

    def get_invoicing_status_response(self) -> BillingInvoicingStatusResponse:
        status_payload = get_billing_invoicing_status()
        return BillingInvoicingStatusResponse(
            enabled=status_payload.enabled,
            ready=status_payload.ready,
            billing_ready=status_payload.billing_ready,
            blockers=list(status_payload.blockers),
        )

    async def list_invoicing_runs(
        self,
        user: User,
        params: BillingInvoicingRunListParams,
    ) -> PaginatedResponse[BillingInvoicingRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        skip = (params.page - 1) * params.page_size
        run_repo = BillingInvoicingRunRepository(self._session)
        runs, total = await run_repo.list_runs(
            organization_id,
            BillingInvoicingRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [BillingInvoicingRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def run_invoicing_cycle(
        self,
        user: User,
        body: BillingInvoicingRunRequest,
    ) -> BillingInvoicingRunResultResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        invoicing_status = get_billing_invoicing_status()
        if not invoicing_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Billing invoicing is not ready",
                    "blockers": list(invoicing_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        summary = await run_billing_invoicing_cycle(
            session=self._session,
            organization_id=organization_id,
            run_kind=body.run_kind,
            performed_by_user_id=user.id,
        )
        if summary.run.status == BillingInvoicingRunStatus.FAILED:
            if self._session is not None:
                await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary.run.error_message or "Billing invoicing run failed",
            )
        if self._session is not None:
            await self._session.commit()
        return BillingInvoicingRunResultResponse(
            completed_at=summary.completed_at,
            run=BillingInvoicingRunResponse.from_model(summary.run),
        )
