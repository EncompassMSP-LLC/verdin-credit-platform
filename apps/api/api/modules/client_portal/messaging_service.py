"""Client portal secure messaging service — scoped to linked cases."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.client_portal.cases_repository import ClientPortalCasesRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client
from api.modules.clients.repository import ClientRepository
from api.modules.messaging.schemas import (
    CaseMessageThreadResponse,
    MessageCreate,
    ThreadMessageResponse,
)
from api.modules.messaging.service import MessagingService


class ClientPortalMessagingService:
    def __init__(self, session: AsyncSession, messaging_service: MessagingService) -> None:
        self._session = session
        self._messaging = messaging_service
        self._cases = ClientPortalCasesRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ClientPortalMessagingService":
        return cls(session, MessagingService.from_session(session))

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

    async def _ensure_case_access(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> None:
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

    async def list_case_messages(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> CaseMessageThreadResponse:
        self._require_enabled()
        await self._ensure_case_access(portal_user, case_id)
        return await self._messaging.get_portal_case_thread(portal_user, case_id)

    async def send_case_message(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        data: MessageCreate,
    ) -> ThreadMessageResponse:
        self._require_enabled()
        await self._ensure_case_access(portal_user, case_id)
        return await self._messaging.post_portal_message(portal_user, case_id, data)
