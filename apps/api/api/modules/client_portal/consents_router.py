"""Client portal consent signing endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.consents_service import ClientPortalConsentsService
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey
from api.modules.compliance.schemas import ConsentRecordResponse, PortalCaseConsentsResponse
from api.modules.documents.storage import DocumentStorage, get_document_storage

router = APIRouter(prefix="/portal/cases", tags=["Client Portal"])


def get_document_storage_dep() -> DocumentStorage:
    return get_document_storage()


def get_portal_consents_service(
    db: AsyncSession = Depends(get_db),
    storage: DocumentStorage = Depends(get_document_storage_dep),
) -> ClientPortalConsentsService:
    return ClientPortalConsentsService.from_session(db, storage)


@router.get("/{case_id}/consents", response_model=PortalCaseConsentsResponse)
async def list_portal_case_consents(
    case_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalConsentsService = Depends(get_portal_consents_service),
) -> PortalCaseConsentsResponse:
    return await service.list_case_consents(portal_user, case_id)


@router.get("/{case_id}/consents/{template_key}/preview")
async def preview_portal_case_consent(
    case_id: uuid.UUID,
    template_key: ConsentDocumentTemplateKey,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalConsentsService = Depends(get_portal_consents_service),
) -> Response:
    pdf_bytes, filename = await service.preview_case_consent(
        portal_user,
        case_id,
        template_key=template_key,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post(
    "/{case_id}/consents/sign",
    response_model=ConsentRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_portal_case_consent(
    case_id: uuid.UUID,
    request: Request,
    template_key: ConsentDocumentTemplateKey = Form(...),
    signer_name: str = Form(...),
    attestation_accepted: bool = Form(...),
    signature_file: UploadFile | None = File(None),
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalConsentsService = Depends(get_portal_consents_service),
) -> ConsentRecordResponse:
    return await service.sign_case_consent(
        portal_user,
        case_id,
        template_key=template_key,
        signer_name=signer_name,
        attestation_accepted=attestation_accepted,
        signature_file=signature_file,
        request=request,
    )
