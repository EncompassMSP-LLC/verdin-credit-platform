"""Public client self-enrollment service."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.client_enrollment import (
    create_stripe_checkout_session,
    get_client_enrollment_settings,
    get_client_enrollment_status,
    retrieve_stripe_checkout_session,
)
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.security import create_portal_access_token, create_portal_refresh_token, hash_password
from api.modules.auth.models import Organization
from api.modules.auth.repository import UserRepository
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.cases.repository import CaseRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.repository import ClientPortalUserRepository
from api.modules.client_portal.schemas import PortalTokenResponse
from api.modules.clients.models import Client, ClientStatus
from api.modules.clients.repository import ClientRepository
from api.modules.enrollment.models import ClientEnrollment, ClientEnrollmentStatus
from api.modules.enrollment.repository import ClientEnrollmentRepository
from api.modules.enrollment.schemas import (
    ClientEnrollmentCheckoutResponse,
    ClientEnrollmentCompleteResponse,
    ClientEnrollmentIntakeRequest,
    ClientEnrollmentSessionResponse,
    ClientEnrollmentStatusResponse,
)


class ClientEnrollmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._enrollments = ClientEnrollmentRepository(session)
        self._clients = ClientRepository(session)
        self._cases = CaseRepository(session)
        self._portal_users = ClientPortalUserRepository(session)
        self._users = UserRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientEnrollmentService:
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_ENROLLMENT):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client enrollment is not enabled",
            )
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def _resolve_organization(self) -> Organization:
        settings = get_client_enrollment_settings()
        result = await self._session.execute(
            select(Organization).where(
                Organization.slug == settings.enrollment_organization_slug,
                Organization.deleted_at.is_(None),
                Organization.is_active.is_(True),
            )
        )
        organization = result.scalar_one_or_none()
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Enrollment organization is not configured",
            )
        return organization

    async def _ensure_email_available(self, email: str) -> None:
        normalized = email.lower()
        existing_portal = await self._portal_users.get_by_email(normalized)
        if existing_portal is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )
        existing_staff = await self._users.get_by_email(normalized)
        if existing_staff is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered",
            )

    def get_status(self) -> ClientEnrollmentStatusResponse:
        self._require_enabled()
        enrollment_status = get_client_enrollment_status()
        return ClientEnrollmentStatusResponse(
            enabled=enrollment_status.enabled,
            ready=enrollment_status.ready,
            payment_required=enrollment_status.payment_required,
            checkout_available=enrollment_status.checkout_available,
            organization_slug=enrollment_status.organization_slug,
            price_id=enrollment_status.price_id,
            annual_credit_report_url=enrollment_status.annual_credit_report_url,
            blockers=enrollment_status.blockers,
        )

    async def start_checkout(
        self,
        body: ClientEnrollmentIntakeRequest,
    ) -> ClientEnrollmentCheckoutResponse:
        self._require_enabled()
        enrollment_status = get_client_enrollment_status()
        if not enrollment_status.checkout_available:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Enrollment checkout is not available",
                    "blockers": enrollment_status.blockers,
                },
            )

        organization = await self._resolve_organization()
        await self._ensure_email_available(body.email)

        enrollment = ClientEnrollment(
            organization_id=organization.id,
            status=ClientEnrollmentStatus.PENDING_PAYMENT,
            email=body.email.lower(),
            hashed_password=hash_password(body.password),
            first_name=body.first_name.strip(),
            last_name=body.last_name.strip(),
            phone=body.phone,
            mailing_address_line1=body.mailing_address_line1.strip(),
            mailing_address_line2=body.mailing_address_line2.strip()
            if body.mailing_address_line2
            else None,
            mailing_city=body.mailing_city.strip(),
            mailing_state=body.mailing_state.strip(),
            mailing_postal_code=body.mailing_postal_code.strip(),
        )
        await self._enrollments.add(enrollment)

        price_id = enrollment_status.price_id
        if price_id is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Enrollment price is not configured",
            )

        try:
            checkout = await create_stripe_checkout_session(
                enrollment_id=str(enrollment.id),
                customer_email=enrollment.email,
                customer_name=f"{enrollment.first_name} {enrollment.last_name}",
                price_id=price_id,
            )
        except ValueError as exc:
            enrollment.status = ClientEnrollmentStatus.FAILED
            enrollment.error_message = str(exc)
            await self._enrollments.save(enrollment)
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to start Stripe checkout",
            ) from exc

        enrollment.stripe_checkout_session_id = checkout.session_id
        await self._enrollments.save(enrollment)
        await self._session.commit()

        return ClientEnrollmentCheckoutResponse(
            enrollment_id=enrollment.id,
            checkout_session_id=checkout.session_id,
            checkout_url=checkout.checkout_url,
        )

    async def register_without_payment(
        self,
        body: ClientEnrollmentIntakeRequest,
    ) -> ClientEnrollmentCompleteResponse:
        self._require_enabled()
        settings = get_client_enrollment_settings()
        if not settings.enrollment_skip_payment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Direct enrollment without payment is disabled",
            )

        organization = await self._resolve_organization()
        await self._ensure_email_available(body.email)

        enrollment = ClientEnrollment(
            organization_id=organization.id,
            status=ClientEnrollmentStatus.PENDING_PAYMENT,
            email=body.email.lower(),
            hashed_password=hash_password(body.password),
            first_name=body.first_name.strip(),
            last_name=body.last_name.strip(),
            phone=body.phone,
            mailing_address_line1=body.mailing_address_line1.strip(),
            mailing_address_line2=body.mailing_address_line2.strip()
            if body.mailing_address_line2
            else None,
            mailing_city=body.mailing_city.strip(),
            mailing_state=body.mailing_state.strip(),
            mailing_postal_code=body.mailing_postal_code.strip(),
        )
        await self._enrollments.add(enrollment)
        await self._session.flush()

        return await self._complete_enrollment_record(
            enrollment,
            payment_status="skipped",
        )

    async def get_checkout_session(self, session_id: str) -> ClientEnrollmentSessionResponse:
        self._require_enabled()
        enrollment = await self._enrollments.get_by_checkout_session_id(session_id)
        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment session not found",
            )
        return self._to_session_response(enrollment)

    async def complete_checkout(self, session_id: str) -> ClientEnrollmentCompleteResponse:
        self._require_enabled()
        enrollment = await self._enrollments.get_by_checkout_session_id(session_id)
        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment session not found",
            )

        if enrollment.status == ClientEnrollmentStatus.COMPLETED and enrollment.portal_user_id:
            portal = await self._portal_users.get_by_id(enrollment.portal_user_id)
            if portal is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Enrollment completed but portal user is missing",
                )
            return ClientEnrollmentCompleteResponse(
                enrollment=self._to_session_response(enrollment),
                portal=self._portal_tokens(portal),
            )

        try:
            checkout_session = await retrieve_stripe_checkout_session(session_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to verify Stripe checkout session",
            ) from exc

        payment_status = str(checkout_session.get("payment_status", ""))
        enrollment.stripe_payment_status = payment_status or None
        if payment_status != "paid":
            await self._enrollments.save(enrollment)
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Payment has not been completed yet",
            )

        return await self._complete_enrollment_record(enrollment, payment_status=payment_status)

    async def handle_checkout_session_completed(self, session_id: str) -> bool:
        enrollment = await self._enrollments.get_by_checkout_session_id(session_id)
        if enrollment is None or enrollment.status == ClientEnrollmentStatus.COMPLETED:
            return False
        try:
            checkout_session = await retrieve_stripe_checkout_session(session_id)
        except ValueError:
            enrollment.status = ClientEnrollmentStatus.FAILED
            enrollment.error_message = "Unable to verify Stripe checkout session"
            await self._enrollments.save(enrollment)
            await self._session.commit()
            return False

        payment_status = str(checkout_session.get("payment_status", ""))
        enrollment.stripe_payment_status = payment_status or None
        if payment_status != "paid":
            return False

        await self._complete_enrollment_record(enrollment, payment_status=payment_status)
        return True

    async def _complete_enrollment_record(
        self,
        enrollment: ClientEnrollment,
        *,
        payment_status: str,
    ) -> ClientEnrollmentCompleteResponse:
        if enrollment.status == ClientEnrollmentStatus.COMPLETED and enrollment.portal_user_id:
            portal = await self._portal_users.get_by_id(enrollment.portal_user_id)
            if portal is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Enrollment completed but portal user is missing",
                )
            return ClientEnrollmentCompleteResponse(
                enrollment=self._to_session_response(enrollment),
                portal=self._portal_tokens(portal),
            )

        display_name = f"{enrollment.first_name} {enrollment.last_name}".strip()
        client = Client(
            organization_id=enrollment.organization_id,
            display_name=display_name,
            email=enrollment.email,
            phone=enrollment.phone,
            mailing_address_line1=enrollment.mailing_address_line1,
            mailing_address_line2=enrollment.mailing_address_line2,
            mailing_city=enrollment.mailing_city,
            mailing_state=enrollment.mailing_state,
            mailing_postal_code=enrollment.mailing_postal_code,
            status=ClientStatus.ACTIVE,
            notes="Created via public client enrollment",
        )
        await self._clients.add(client)

        case = Case(
            organization_id=enrollment.organization_id,
            client_id=client.id,
            title=f"Credit repair — {display_name}",
            client_name=display_name,
            client_email=enrollment.email,
            case_number=f"ENR-{enrollment.id.hex[:8].upper()}",
            status=CaseStatus.OPEN,
            stage=CaseStage.INTAKE,
            priority=CasePriority.MEDIUM,
            summary=(
                "Client enrolled online. Next steps: sign compliance documents, "
                "pull credit reports from annualcreditreport.com, and upload PDFs."
            ),
            opened_at=datetime.now(UTC),
        )
        await self._cases.create(case)

        portal_user = ClientPortalUser(
            organization_id=enrollment.organization_id,
            client_id=client.id,
            email=enrollment.email,
            hashed_password=enrollment.hashed_password,
            is_active=True,
        )
        await self._portal_users.add(portal_user)

        enrollment.status = ClientEnrollmentStatus.COMPLETED
        enrollment.stripe_payment_status = payment_status
        enrollment.client_id = client.id
        enrollment.case_id = case.id
        enrollment.portal_user_id = portal_user.id
        enrollment.completed_at = datetime.now(UTC)
        enrollment.error_message = None
        await self._enrollments.save(enrollment)
        await self._session.commit()
        await self._session.refresh(portal_user)

        return ClientEnrollmentCompleteResponse(
            enrollment=self._to_session_response(enrollment),
            portal=self._portal_tokens(portal_user),
        )

    @staticmethod
    def _portal_tokens(portal_user: ClientPortalUser) -> PortalTokenResponse:
        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    @staticmethod
    def _to_session_response(enrollment: ClientEnrollment) -> ClientEnrollmentSessionResponse:
        return ClientEnrollmentSessionResponse(
            enrollment_id=enrollment.id,
            status=enrollment.status.value,
            payment_status=enrollment.stripe_payment_status,
            case_id=enrollment.case_id,
            client_id=enrollment.client_id,
            completed_at=enrollment.completed_at,
            error_message=enrollment.error_message,
        )
