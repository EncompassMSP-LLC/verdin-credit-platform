"""Weekly partner status digest service (LRP-207)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.email_delivery import (
    EmailDeliveryNotReadyError,
    EmailMessage,
    require_email_delivery_ready,
    send_email_message,
)
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.mortgage_partner.models import (
    LoanPipelineStage,
    OrgPartnership,
)
from api.modules.mortgage_partner.permissions import (
    MORTGAGE_PARTNER_READ_ROLE,
    MORTGAGE_PARTNER_WRITE_ROLE,
)
from api.modules.mortgage_partner.repository import MortgagePartnerRepository
from api.modules.mortgage_partner.schemas import (
    WeeklyDigestProcessResponse,
    WeeklyDigestRunResponse,
    WeeklyDigestSubscriptionCreate,
    WeeklyDigestSubscriptionResponse,
    WeeklyDigestSubscriptionUpdate,
)
from api.modules.mortgage_partner.weekly_digest_models import (
    PartnerWeeklyDigestRun,
    PartnerWeeklyDigestSubscription,
)
from api.modules.notifications.notification_matrix import advisory_footer

SCHEMA_VERSION = "partner-weekly-digest.v1"
_ADVISORY = advisory_footer()
_STALL_DAYS = 7
_ACTIVE_STAGES = frozenset(
    {
        LoanPipelineStage.REFERRED,
        LoanPipelineStage.INTAKE,
        LoanPipelineStage.IN_REPAIR,
        LoanPipelineStage.NEAR_READY,
        LoanPipelineStage.MORTGAGE_READY,
        LoanPipelineStage.IN_UNDERWRITING,
    }
)


def iso_week_key(when: datetime) -> str:
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    iso = when.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def borrower_initials(display_name: str | None) -> str:
    if not display_name or not display_name.strip():
        return "—"
    parts = [p for p in display_name.strip().split() if p]
    if len(parts) == 1:
        return (parts[0][:1] + ".").upper()
    return f"{parts[0][:1]}.{parts[-1][:1]}.".upper()


class PartnerWeeklyDigestService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = MortgagePartnerRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> PartnerWeeklyDigestService:
        return cls(session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, MORTGAGE_PARTNER_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view mortgage partner resources",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, MORTGAGE_PARTNER_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage mortgage partner resources",
            )

    def _sub_to_response(
        self, row: PartnerWeeklyDigestSubscription
    ) -> WeeklyDigestSubscriptionResponse:
        return WeeklyDigestSubscriptionResponse(
            id=row.id,
            organization_id=row.organization_id,
            partnership_id=row.partnership_id,
            recipient_name=row.recipient_name,
            recipient_email=row.recipient_email,
            enabled=row.enabled,
            marketing_opt_in=row.marketing_opt_in,
            send_weekday=row.send_weekday,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _run_to_response(self, row: PartnerWeeklyDigestRun) -> WeeklyDigestRunResponse:
        return WeeklyDigestRunResponse(
            id=row.id,
            organization_id=row.organization_id,
            partnership_id=row.partnership_id,
            subscription_id=row.subscription_id,
            week_key=row.week_key,
            status=row.status,
            schema_version=row.schema_version,
            attempted_at=row.attempted_at,
            payload=row.payload,
            body_text=row.body_text,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def list_subscriptions(self, user: User) -> list[WeeklyDigestSubscriptionResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        result = await self._session.execute(
            select(PartnerWeeklyDigestSubscription)
            .where(
                PartnerWeeklyDigestSubscription.organization_id == organization_id,
                PartnerWeeklyDigestSubscription.deleted_at.is_(None),
            )
            .order_by(PartnerWeeklyDigestSubscription.created_at.desc())
        )
        return [self._sub_to_response(row) for row in result.scalars().all()]

    async def create_subscription(
        self,
        user: User,
        payload: WeeklyDigestSubscriptionCreate,
    ) -> WeeklyDigestSubscriptionResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        partnership = await self._repo.get_partnership(payload.partnership_id, organization_id)
        if partnership is None:
            raise HTTPException(status_code=404, detail="Partnership not found")
        if not payload.marketing_opt_in:
            raise HTTPException(
                status_code=400,
                detail="marketing_opt_in is required for weekly digest subscriptions",
            )
        if payload.send_weekday < 1 or payload.send_weekday > 7:
            raise HTTPException(status_code=422, detail="send_weekday must be 1–7 (ISO)")

        row = PartnerWeeklyDigestSubscription(
            id=uuid.uuid4(),
            organization_id=organization_id,
            partnership_id=payload.partnership_id,
            recipient_name=payload.recipient_name,
            recipient_email=str(payload.recipient_email).lower(),
            enabled=True,
            marketing_opt_in=True,
            send_weekday=payload.send_weekday,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return self._sub_to_response(row)

    async def update_subscription(
        self,
        user: User,
        subscription_id: uuid.UUID,
        payload: WeeklyDigestSubscriptionUpdate,
    ) -> WeeklyDigestSubscriptionResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        row = await self._get_subscription(subscription_id, organization_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Digest subscription not found")

        data = payload.model_dump(exclude_unset=True)
        if "marketing_opt_in" in data and data["marketing_opt_in"] is False:
            row.marketing_opt_in = False
            row.enabled = False
        if "enabled" in data and data["enabled"] is not None:
            row.enabled = bool(data["enabled"])
        if "recipient_name" in data and data["recipient_name"] is not None:
            row.recipient_name = data["recipient_name"]
        if "send_weekday" in data and data["send_weekday"] is not None:
            weekday = int(data["send_weekday"])
            if weekday < 1 or weekday > 7:
                raise HTTPException(status_code=422, detail="send_weekday must be 1–7 (ISO)")
            row.send_weekday = weekday
        row.updated_by_id = user.id
        await self._session.commit()
        await self._session.refresh(row)
        return self._sub_to_response(row)

    async def list_runs(
        self,
        user: User,
        *,
        partnership_id: uuid.UUID | None = None,
    ) -> list[WeeklyDigestRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        stmt = (
            select(PartnerWeeklyDigestRun)
            .where(PartnerWeeklyDigestRun.organization_id == organization_id)
            .order_by(PartnerWeeklyDigestRun.attempted_at.desc())
            .limit(100)
        )
        if partnership_id is not None:
            stmt = stmt.where(PartnerWeeklyDigestRun.partnership_id == partnership_id)
        result = await self._session.execute(stmt)
        return [self._run_to_response(row) for row in result.scalars().all()]

    async def process_due(
        self,
        user: User,
        *,
        week_key: str | None = None,
        force: bool = True,
    ) -> WeeklyDigestProcessResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        now = datetime.now(UTC)
        key = week_key or iso_week_key(now)
        runs = await self._process_internal(
            organization_id=organization_id,
            week_key=key,
            now=now,
            force_weekday=force,
        )
        await self._session.commit()
        return WeeklyDigestProcessResponse(
            processed_count=len(runs),
            week_key=key,
            runs=[self._run_to_response(run) for run in runs],
        )

    async def _process_internal(
        self,
        *,
        organization_id: uuid.UUID,
        week_key: str,
        now: datetime,
        force_weekday: bool,
    ) -> list[PartnerWeeklyDigestRun]:
        result = await self._session.execute(
            select(PartnerWeeklyDigestSubscription).where(
                PartnerWeeklyDigestSubscription.organization_id == organization_id,
                PartnerWeeklyDigestSubscription.deleted_at.is_(None),
                PartnerWeeklyDigestSubscription.enabled.is_(True),
                PartnerWeeklyDigestSubscription.marketing_opt_in.is_(True),
            )
        )
        runs: list[PartnerWeeklyDigestRun] = []
        iso_weekday = now.isocalendar().weekday
        for sub in result.scalars().all():
            if not force_weekday and sub.send_weekday != iso_weekday:
                continue
            existing = await self._find_run(sub.id, week_key)
            if existing is not None:
                runs.append(existing)
                continue
            run = await self._deliver_subscription(sub, week_key=week_key, now=now)
            if run is not None:
                runs.append(run)
        return runs

    async def _deliver_subscription(
        self,
        sub: PartnerWeeklyDigestSubscription,
        *,
        week_key: str,
        now: datetime,
    ) -> PartnerWeeklyDigestRun | None:
        partnership = await self._repo.get_partnership(sub.partnership_id, sub.organization_id)
        if partnership is None:
            return None

        snapshot = await self._compose_snapshot(partnership, week_key=week_key, now=now)
        body = self._render_body(partnership, sub, snapshot, week_key=week_key)
        delivery_status, delivery_meta = await self._send_email(sub, body, week_key=week_key)

        run = PartnerWeeklyDigestRun(
            id=uuid.uuid4(),
            organization_id=sub.organization_id,
            partnership_id=sub.partnership_id,
            subscription_id=sub.id,
            week_key=week_key,
            status=delivery_status,
            schema_version=SCHEMA_VERSION,
            attempted_at=now,
            body_text=body,
            payload={
                **snapshot,
                **delivery_meta,
                "recipient_email": sub.recipient_email,
                "claim_safety": {
                    "auto_filing": False,
                    "underwriting_decision": False,
                    "pii_minimized": True,
                    "advisory_footer": _ADVISORY,
                },
            },
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def _compose_snapshot(
        self,
        partnership: OrgPartnership,
        *,
        week_key: str,
        now: datetime,
    ) -> dict[str, Any]:
        referrals = await self._repo.list_pipeline_referrals(
            partnership.id, partnership.cro_organization_id
        )
        counts = self._repo.compute_dashboard_summary(referrals)
        names = await self._repo.map_client_display_names(
            partnership.cro_organization_id,
            [r.client_id for r in referrals],
        )
        week_start = now - timedelta(days=now.isocalendar().weekday - 1)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        if week_start.tzinfo is None:
            week_start = week_start.replace(tzinfo=UTC)

        movement: list[dict[str, Any]] = []
        needs_attention: list[dict[str, Any]] = []
        for ref in referrals:
            initials = borrower_initials(names.get(ref.client_id))
            changed = ref.pipeline_stage_changed_at
            if changed is not None:
                if changed.tzinfo is None:
                    changed = changed.replace(tzinfo=UTC)
                if changed >= week_start:
                    movement.append(
                        {
                            "referral_id": str(ref.id),
                            "borrower_initials": initials,
                            "stage": ref.pipeline_stage.value,
                            "changed_at": changed.isoformat(),
                            "note": "Stage update (PII-minimized)",
                        }
                    )
            if (
                ref.pipeline_stage in _ACTIVE_STAGES
                and changed is not None
                and (now - changed).days >= _STALL_DAYS
            ):
                needs_attention.append(
                    {
                        "referral_id": str(ref.id),
                        "borrower_initials": initials,
                        "issue": "docs_or_stage_stalled",
                        "stage": ref.pipeline_stage.value,
                        "days_in_stage": (now - changed).days,
                        "next_action_hint": "Staff follow-up",
                    }
                )

        funded_wtd = sum(
            1
            for r in referrals
            if r.pipeline_stage is LoanPipelineStage.FUNDED
            and r.pipeline_stage_changed_at is not None
            and (
                r.pipeline_stage_changed_at.replace(tzinfo=UTC)
                if r.pipeline_stage_changed_at.tzinfo is None
                else r.pipeline_stage_changed_at
            )
            >= week_start
        )
        lost_wtd = sum(
            1
            for r in referrals
            if r.pipeline_stage in {LoanPipelineStage.DECLINED, LoanPipelineStage.WITHDRAWN}
            and r.pipeline_stage_changed_at is not None
            and (
                r.pipeline_stage_changed_at.replace(tzinfo=UTC)
                if r.pipeline_stage_changed_at.tzinfo is None
                else r.pipeline_stage_changed_at
            )
            >= week_start
        )

        return {
            "week_key": week_key,
            "partner_label": partnership.display_name or partnership.partner_type.value,
            "pipeline_snapshot": counts,
            "total_referrals": len(referrals),
            "funded_wtd": funded_wtd,
            "lost_wtd": lost_wtd,
            "movement": movement[:25],
            "needs_attention": needs_attention[:25],
            "wins": [
                {
                    "label": "mortgage_ready_hand_back",
                    "count": counts.get(LoanPipelineStage.MORTGAGE_READY.value, 0),
                }
            ],
        }

    def _render_body(
        self,
        partnership: OrgPartnership,
        sub: PartnerWeeklyDigestSubscription,
        snapshot: dict[str, Any],
        *,
        week_key: str,
    ) -> str:
        partner = snapshot.get("partner_label") or "Partner"
        lines = [
            f"Weekly partner status digest — {partner}",
            f"Week of {week_key}",
            f"Prepared for {sub.recipient_name}",
            "",
            "Pipeline snapshot (counts by stage):",
        ]
        for stage, count in sorted((snapshot.get("pipeline_snapshot") or {}).items()):
            lines.append(f"  - {stage}: {count}")
        lines.append(f"  - funded (WTD): {snapshot.get('funded_wtd', 0)}")
        lines.append(f"  - lost / withdrawn (WTD): {snapshot.get('lost_wtd', 0)}")
        lines.append("")
        lines.append("Movement this week (initials only):")
        movement = snapshot.get("movement") or []
        if not movement:
            lines.append("  - None recorded")
        else:
            for row in movement:
                lines.append(
                    f"  - {row['borrower_initials']} → {row['stage']} ({row['referral_id'][:8]}…)"
                )
        lines.append("")
        lines.append("Needs attention:")
        attention = snapshot.get("needs_attention") or []
        if not attention:
            lines.append("  - None")
        else:
            for row in attention:
                lines.append(
                    f"  - {row['borrower_initials']} · {row['issue']} · "
                    f"{row['days_in_stage']}d in {row['stage']}"
                )
        lines.append("")
        lines.append("Wins (claim-safe workflow only — no score or approval claims):")
        for win in snapshot.get("wins") or []:
            lines.append(f"  - {win['label']}: {win['count']}")
        lines.append("")
        lines.append(_ADVISORY)
        return "\n".join(lines)

    async def _send_email(
        self,
        sub: PartnerWeeklyDigestSubscription,
        body: str,
        *,
        week_key: str,
    ) -> tuple[str, dict[str, Any]]:
        try:
            require_email_delivery_ready()
        except EmailDeliveryNotReadyError as exc:
            return "deferred_email_not_ready", {"blockers": list(exc.blockers)}
        result = await send_email_message(
            EmailMessage(
                to=sub.recipient_email,
                subject=f"Weekly lending-readiness digest — {week_key}",
                body_text=body,
            )
        )
        return (
            "sent" if result.success else "failed",
            {
                "provider_message_id": result.provider_message_id,
                "error": result.error,
            },
        )

    async def _get_subscription(
        self,
        subscription_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> PartnerWeeklyDigestSubscription | None:
        result = await self._session.execute(
            select(PartnerWeeklyDigestSubscription).where(
                PartnerWeeklyDigestSubscription.id == subscription_id,
                PartnerWeeklyDigestSubscription.organization_id == organization_id,
                PartnerWeeklyDigestSubscription.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def _find_run(
        self,
        subscription_id: uuid.UUID,
        week_key: str,
    ) -> PartnerWeeklyDigestRun | None:
        result = await self._session.execute(
            select(PartnerWeeklyDigestRun).where(
                PartnerWeeklyDigestRun.subscription_id == subscription_id,
                PartnerWeeklyDigestRun.week_key == week_key,
            )
        )
        return result.scalar_one_or_none()
