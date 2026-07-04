"""SMS marketing campaign delivery for the background worker."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from worker.sms_marketing_tables import (
    sms_delivery_logs_table,
    sms_marketing_campaign_runs_table,
    users_table,
)

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
DELIVERY_SENT = "sent"
DELIVERY_FAILED = "failed"


@dataclass(frozen=True, slots=True)
class SmsMarketingCampaignDeliveryResult:
    messages_sent: int
    messages_failed: int
    status: str
    error_message: str | None = None


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "false").lower() in ("true", "1", "yes")


def _delivery_blockers() -> list[str]:
    blockers: list[str] = []
    if not _env_enabled("ENABLE_SMS_MARKETING_DELIVERY"):
        blockers.append("ENABLE_SMS_MARKETING_DELIVERY is false")
    if not _env_enabled("ENABLE_SMS_DELIVERY"):
        blockers.append("ENABLE_SMS_DELIVERY is false")
    if os.getenv("SMS_PROVIDER", "none").lower() != "twilio":
        blockers.append("SMS_PROVIDER is not configured")
    if not os.getenv("SMS_FROM_NUMBER"):
        blockers.append("SMS_FROM_NUMBER is not configured")
    if not os.getenv("SMS_TWILIO_ACCOUNT_SID"):
        blockers.append("SMS_TWILIO_ACCOUNT_SID is not configured for twilio provider")
    if not os.getenv("SMS_TWILIO_AUTH_TOKEN"):
        blockers.append("SMS_TWILIO_AUTH_TOKEN is not configured for twilio provider")
    return blockers


def _send_twilio_message(
    *, to: str, body: str, from_number: str
) -> tuple[bool, str | None, str | None]:
    account_sid = os.getenv("SMS_TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("SMS_TWILIO_AUTH_TOKEN", "")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    payload = {"To": to, "From": from_number, "Body": body}

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, auth=(account_sid, auth_token), data=payload)
        if response.status_code >= 400:
            return False, None, response.text
        data = response.json()
        return True, data.get("sid"), None
    except Exception as exc:  # noqa: BLE001 — provider errors surfaced to audit log
        return False, None, str(exc)


def deliver_sms_marketing_campaign_run(
    session: Session,
    *,
    campaign_run_id: uuid.UUID,
) -> SmsMarketingCampaignDeliveryResult:
    run_row = (
        session.execute(
            select(sms_marketing_campaign_runs_table).where(
                sms_marketing_campaign_runs_table.c.id == campaign_run_id
            )
        )
        .mappings()
        .one_or_none()
    )
    if run_row is None:
        return SmsMarketingCampaignDeliveryResult(
            messages_sent=0,
            messages_failed=0,
            status=STATUS_FAILED,
            error_message=f"Campaign run {campaign_run_id} not found",
        )

    if run_row["status"] not in (STATUS_PENDING, STATUS_RUNNING):
        return SmsMarketingCampaignDeliveryResult(
            messages_sent=int(run_row["messages_sent"]),
            messages_failed=int(run_row["messages_failed"]),
            status=str(run_row["status"]),
            error_message=run_row["error_message"],
        )

    started_at = run_row["started_at"] or datetime.now(UTC)
    session.execute(
        update(sms_marketing_campaign_runs_table)
        .where(sms_marketing_campaign_runs_table.c.id == campaign_run_id)
        .values(status=STATUS_RUNNING, started_at=started_at)
    )

    blockers = _delivery_blockers()
    messages_sent = 0
    messages_failed = 0
    run_error: str | None = "; ".join(blockers) if blockers else None
    provider = os.getenv("SMS_PROVIDER", "none")
    from_number = os.getenv("SMS_FROM_NUMBER", "")

    if not blockers:
        for user_id_raw in run_row["recipient_user_ids"] or []:
            user_id = uuid.UUID(str(user_id_raw))
            recipient = (
                session.execute(select(users_table).where(users_table.c.id == user_id))
                .mappings()
                .one_or_none()
            )
            if (
                recipient is None
                or recipient["organization_id"] != run_row["organization_id"]
            ):
                messages_failed += 1
                continue
            phone_number = recipient["phone_number"]
            if not phone_number:
                messages_failed += 1
                continue

            success, provider_message_id, error_message = _send_twilio_message(
                to=phone_number,
                body=str(run_row["message_body"]),
                from_number=from_number,
            )
            if success:
                messages_sent += 1
            else:
                messages_failed += 1

            now = datetime.now(UTC)
            session.execute(
                insert(sms_delivery_logs_table).values(
                    id=uuid.uuid4(),
                    organization_id=run_row["organization_id"],
                    recipient_user_id=user_id,
                    recipient_phone=phone_number,
                    body=str(run_row["message_body"]),
                    provider=provider,
                    status=DELIVERY_SENT if success else DELIVERY_FAILED,
                    provider_message_id=provider_message_id,
                    error_message=error_message,
                    sent_by_user_id=run_row["performed_by_user_id"],
                    campaign_run_id=campaign_run_id,
                    created_at=now,
                    updated_at=now,
                )
            )

    completed_at = datetime.now(UTC)
    final_status = (
        STATUS_FAILED if run_error and messages_sent == 0 else STATUS_COMPLETED
    )
    session.execute(
        update(sms_marketing_campaign_runs_table)
        .where(sms_marketing_campaign_runs_table.c.id == campaign_run_id)
        .values(
            status=final_status,
            messages_sent=messages_sent,
            messages_failed=messages_failed,
            completed_at=completed_at,
            error_message=run_error,
        )
    )

    return SmsMarketingCampaignDeliveryResult(
        messages_sent=messages_sent,
        messages_failed=messages_failed,
        status=final_status,
        error_message=run_error,
    )
