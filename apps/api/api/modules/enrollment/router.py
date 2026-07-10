"""Public client enrollment endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.enrollment.schemas import (
    ClientEnrollmentCheckoutResponse,
    ClientEnrollmentCompleteRequest,
    ClientEnrollmentCompleteResponse,
    ClientEnrollmentIntakeRequest,
    ClientEnrollmentSessionResponse,
    ClientEnrollmentStatusResponse,
)
from api.modules.enrollment.service import ClientEnrollmentService

router = APIRouter(prefix="/enrollment", tags=["Client Enrollment"])


def get_enrollment_service(db: AsyncSession = Depends(get_db)) -> ClientEnrollmentService:
    return ClientEnrollmentService.from_session(db)


@router.get("/status", response_model=ClientEnrollmentStatusResponse)
async def get_enrollment_status(
    service: ClientEnrollmentService = Depends(get_enrollment_service),
) -> ClientEnrollmentStatusResponse:
    return service.get_status()


@router.post("/checkout", response_model=ClientEnrollmentCheckoutResponse, status_code=201)
async def start_enrollment_checkout(
    body: ClientEnrollmentIntakeRequest,
    service: ClientEnrollmentService = Depends(get_enrollment_service),
) -> ClientEnrollmentCheckoutResponse:
    return await service.start_checkout(body)


@router.post("/register", response_model=ClientEnrollmentCompleteResponse, status_code=201)
async def register_without_payment(
    body: ClientEnrollmentIntakeRequest,
    service: ClientEnrollmentService = Depends(get_enrollment_service),
) -> ClientEnrollmentCompleteResponse:
    return await service.register_without_payment(body)


@router.get("/checkout/{session_id}", response_model=ClientEnrollmentSessionResponse)
async def get_enrollment_checkout_session(
    session_id: str,
    service: ClientEnrollmentService = Depends(get_enrollment_service),
) -> ClientEnrollmentSessionResponse:
    return await service.get_checkout_session(session_id)


@router.post("/complete", response_model=ClientEnrollmentCompleteResponse)
async def complete_enrollment_checkout(
    body: ClientEnrollmentCompleteRequest,
    service: ClientEnrollmentService = Depends(get_enrollment_service),
) -> ClientEnrollmentCompleteResponse:
    return await service.complete_checkout(body.session_id)
