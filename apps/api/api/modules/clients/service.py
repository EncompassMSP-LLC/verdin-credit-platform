"""Client management service — business logic for clients and contacts."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.clients.communication_preferences import (
    DNC_DISCLOSURE,
    OFFICIAL_DNC_REGISTRY_URL,
    PREFERENCES_DISCLAIMER,
    append_preference_event,
    build_communication_request_draft,
    default_preferences,
    followup_due_from,
)
from api.modules.clients.models import (
    Client,
    ClientCommunicationPreferences,
    ClientContact,
    DncAssistanceStatus,
)
from api.modules.clients.permissions import CLIENT_DELETE_ROLE, CLIENT_WRITE_ROLE
from api.modules.clients.repository import (
    ClientContactListFilters,
    ClientListFilters,
    ClientRepository,
)
from api.modules.clients.schemas import (
    ClientCommunicationPreferencesResponse,
    ClientCommunicationPreferencesUpdate,
    ClientContactCreate,
    ClientContactListParams,
    ClientContactResponse,
    ClientContactUpdate,
    ClientCreate,
    ClientListParams,
    ClientResponse,
    ClientUpdate,
    PreferenceEventItem,
)


class ClientService:
    def __init__(self, client_repo: ClientRepository, session: AsyncSession | None = None) -> None:
        self._clients = client_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ClientService":
        return cls(ClientRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CLIENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify clients",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, CLIENT_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete clients",
            )

    async def _get_client_for_user(self, client_id: uuid.UUID, user: User) -> Client:
        organization_id = self._require_organization(user)
        client = await self._clients.get_by_id(client_id, organization_id=organization_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    async def create_client(self, user: User, data: ClientCreate) -> ClientResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)

        client = Client(
            organization_id=organization_id,
            display_name=data.display_name,
            email=str(data.email) if data.email else None,
            phone=data.phone,
            mailing_address_line1=data.mailing_address_line1,
            mailing_address_line2=data.mailing_address_line2,
            mailing_city=data.mailing_city,
            mailing_state=data.mailing_state,
            mailing_postal_code=data.mailing_postal_code,
            status=data.status,
            notes=data.notes,
        )
        apply_audit_on_create(client, user.id)
        await self._clients.add(client)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(client)
        return ClientResponse.from_model(client)

    async def list_clients(
        self, user: User, params: ClientListParams
    ) -> PaginatedResponse[ClientResponse]:
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        items, total = await self._clients.list_clients(
            ClientListFilters(
                organization_id=organization_id,
                search=params.search,
                status=params.status,
                skip=skip,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        return paginate(
            [ClientResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_client(self, user: User, client_id: uuid.UUID) -> ClientResponse:
        client = await self._get_client_for_user(client_id, user)
        return ClientResponse.from_model(client)

    async def update_client(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientUpdate,
    ) -> ClientResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)

        updates = data.model_dump(exclude_unset=True)
        if "email" in updates:
            updates["email"] = str(updates["email"]) if updates["email"] is not None else None
        for key, value in updates.items():
            setattr(client, key, value)
        apply_audit_on_update(client, user.id)
        await self._clients.save(client)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(client)
        return ClientResponse.from_model(client)

    async def delete_client(self, user: User, client_id: uuid.UUID) -> None:
        self._require_delete(user)
        client = await self._get_client_for_user(client_id, user)
        await self._clients.cascade_soft_delete_related(
            organization_id=client.organization_id,
            client_id=client.id,
            updated_by_id=user.id,
        )
        client.soft_delete()
        apply_audit_on_update(client, user.id)
        await self._clients.save(client)
        if self._session is not None:
            await self._session.commit()

    async def create_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientContactCreate,
    ) -> ClientContactResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)

        if data.is_primary:
            await self._clients.clear_primary_contacts(
                organization_id=client.organization_id,
                client_id=client.id,
            )

        contact = ClientContact(
            organization_id=client.organization_id,
            client_id=client.id,
            full_name=data.full_name,
            email=str(data.email) if data.email else None,
            phone=data.phone,
            relationship_type=data.relationship_type,
            is_primary=data.is_primary,
            notes=data.notes,
        )
        apply_audit_on_create(contact, user.id)
        await self._clients.add_contact(contact)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(contact)
        return ClientContactResponse.from_model(contact)

    async def list_contacts(
        self,
        user: User,
        client_id: uuid.UUID,
        params: ClientContactListParams,
    ) -> PaginatedResponse[ClientContactResponse]:
        client = await self._get_client_for_user(client_id, user)
        skip = (params.page - 1) * params.page_size
        items, total = await self._clients.list_contacts(
            ClientContactListFilters(
                organization_id=client.organization_id,
                client_id=client.id,
                search=params.search,
                relationship_type=params.relationship_type,
                is_primary=params.is_primary,
                skip=skip,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        return paginate(
            [ClientContactResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> ClientContactResponse:
        client = await self._get_client_for_user(client_id, user)
        contact = await self._clients.get_contact_by_id(
            contact_id,
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return ClientContactResponse.from_model(contact)

    async def update_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        contact_id: uuid.UUID,
        data: ClientContactUpdate,
    ) -> ClientContactResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        contact = await self._clients.get_contact_by_id(
            contact_id,
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )

        updates = data.model_dump(exclude_unset=True)
        if updates.get("is_primary"):
            await self._clients.clear_primary_contacts(
                organization_id=client.organization_id,
                client_id=client.id,
                except_contact_id=contact.id,
            )
        if "email" in updates:
            updates["email"] = str(updates["email"]) if updates["email"] is not None else None
        for key, value in updates.items():
            setattr(contact, key, value)
        apply_audit_on_update(contact, user.id)
        await self._clients.save_contact(contact)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(contact)
        return ClientContactResponse.from_model(contact)

    async def delete_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> None:
        self._require_delete(user)
        client = await self._get_client_for_user(client_id, user)
        contact = await self._clients.get_contact_by_id(
            contact_id,
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        contact.soft_delete()
        apply_audit_on_update(contact, user.id)
        await self._clients.save_contact(contact)
        if self._session is not None:
            await self._session.commit()

    def _preferences_response(
        self,
        client: Client,
        prefs: ClientCommunicationPreferences,
    ) -> ClientCommunicationPreferencesResponse:
        events = [
            PreferenceEventItem(
                at=str(item.get("at") or ""),
                action=str(item.get("action") or ""),
                actor_id=item.get("actor_id"),
                detail=item.get("detail"),
            )
            for item in (prefs.preference_events or [])
            if isinstance(item, dict)
        ]
        return ClientCommunicationPreferencesResponse(
            id=prefs.id,
            organization_id=prefs.organization_id,
            client_id=prefs.client_id,
            preferred_channel=prefs.preferred_channel,
            do_not_text=prefs.do_not_text,
            do_not_email=prefs.do_not_email,
            best_calling_hours=prefs.best_calling_hours,
            workplace_calls_prohibited=prefs.workplace_calls_prohibited,
            attorney_representation_status=prefs.attorney_representation_status,
            collector_opt_out_recorded=prefs.collector_opt_out_recorded,
            collector_opt_out_recorded_at=prefs.collector_opt_out_recorded_at,
            dnc_assistance_requested=prefs.dnc_assistance_requested,
            dnc_consent_attested=prefs.dnc_consent_attested,
            dnc_phone_ownership_confirmed=prefs.dnc_phone_ownership_confirmed,
            dnc_disclosure_acknowledged=prefs.dnc_disclosure_acknowledged,
            dnc_phone_number=prefs.dnc_phone_number,
            dnc_status=prefs.dnc_status,
            dnc_registry_opened_at=prefs.dnc_registry_opened_at,
            dnc_completed_at=prefs.dnc_completed_at,
            dnc_followup_due_at=prefs.dnc_followup_due_at,
            preference_events=events,
            notes=prefs.notes,
            official_dnc_registry_url=OFFICIAL_DNC_REGISTRY_URL,
            dnc_disclosure=DNC_DISCLOSURE,
            disclaimer=PREFERENCES_DISCLAIMER,
            communication_request_draft=build_communication_request_draft(client, prefs),
            created_at=prefs.created_at,
            updated_at=prefs.updated_at,
        )

    async def _get_or_create_preferences(
        self,
        user: User,
        client: Client,
    ) -> ClientCommunicationPreferences:
        prefs = await self._clients.get_communication_preferences(
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if prefs is not None:
            return prefs
        prefs = default_preferences(
            organization_id=client.organization_id,
            client_id=client.id,
        )
        apply_audit_on_create(prefs, user.id)
        append_preference_event(
            prefs,
            action="created",
            actor_id=str(user.id),
            detail="Default communication preferences created",
        )
        await self._clients.add_communication_preferences(prefs)
        return prefs

    async def get_communication_preferences(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientCommunicationPreferencesResponse:
        client = await self._get_client_for_user(client_id, user)
        prefs = await self._get_or_create_preferences(user, client)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(prefs)
        return self._preferences_response(client, prefs)

    async def update_communication_preferences(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientCommunicationPreferencesUpdate,
    ) -> ClientCommunicationPreferencesResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        prefs = await self._get_or_create_preferences(user, client)
        updates = data.model_dump(exclude_unset=True)

        if (
            updates.get("collector_opt_out_recorded") is True
            and not prefs.collector_opt_out_recorded
        ):
            from datetime import UTC, datetime

            prefs.collector_opt_out_recorded_at = datetime.now(UTC)
        if updates.get("collector_opt_out_recorded") is False:
            prefs.collector_opt_out_recorded_at = None

        for key, value in updates.items():
            setattr(prefs, key, value)

        if (
            prefs.dnc_assistance_requested
            and prefs.dnc_consent_attested
            and prefs.dnc_phone_ownership_confirmed
            and prefs.dnc_disclosure_acknowledged
            and prefs.dnc_status == DncAssistanceStatus.NOT_STARTED
        ):
            prefs.dnc_status = DncAssistanceStatus.CONSENT_RECORDED

        apply_audit_on_update(prefs, user.id)
        append_preference_event(
            prefs,
            action="updated",
            actor_id=str(user.id),
            detail=", ".join(sorted(updates.keys())) or None,
        )
        await self._clients.save_communication_preferences(prefs)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(prefs)
        return self._preferences_response(client, prefs)

    async def open_dnc_registry(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientCommunicationPreferencesResponse:
        """Record that the official registry workflow was opened — never auto-submits."""
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        prefs = await self._get_or_create_preferences(user, client)
        if not (
            prefs.dnc_assistance_requested
            and prefs.dnc_consent_attested
            and prefs.dnc_phone_ownership_confirmed
            and prefs.dnc_disclosure_acknowledged
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Do Not Call assistance requires explicit request, consent, "
                    "phone-ownership confirmation, and disclosure acknowledgment"
                ),
            )
        if not prefs.dnc_phone_number:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A phone number is required before opening the registry workflow",
            )
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        prefs.dnc_registry_opened_at = now
        prefs.dnc_status = DncAssistanceStatus.AWAITING_EMAIL_CONFIRMATION
        apply_audit_on_update(prefs, user.id)
        append_preference_event(
            prefs,
            action="dnc_registry_opened",
            actor_id=str(user.id),
            detail=f"Official registry URL provided: {OFFICIAL_DNC_REGISTRY_URL}",
        )
        await self._clients.save_communication_preferences(prefs)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(prefs)
        return self._preferences_response(client, prefs)

    async def mark_dnc_completed(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientCommunicationPreferencesResponse:
        """Client/staff attestation that registry confirmation finished — never invents completion."""
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        prefs = await self._get_or_create_preferences(user, client)
        if prefs.dnc_status not in {
            DncAssistanceStatus.REGISTRY_LINK_OPENED,
            DncAssistanceStatus.AWAITING_EMAIL_CONFIRMATION,
            DncAssistanceStatus.CONSENT_RECORDED,
        }:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Do Not Call registration can only be marked complete after consent "
                    "and registry assistance have started"
                ),
            )
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        prefs.dnc_completed_at = now
        prefs.dnc_followup_due_at = followup_due_from(now)
        prefs.dnc_status = DncAssistanceStatus.COMPLETED
        apply_audit_on_update(prefs, user.id)
        append_preference_event(
            prefs,
            action="dnc_marked_completed",
            actor_id=str(user.id),
            detail="Client/staff marked National Do Not Call registration complete",
        )
        await self._clients.save_communication_preferences(prefs)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(prefs)
        return self._preferences_response(client, prefs)
