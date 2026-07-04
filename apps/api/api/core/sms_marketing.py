"""SMS marketing campaign readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.sms_delivery import get_sms_delivery_status


@dataclass(frozen=True)
class SmsMarketingCampaignStatus:
    enabled: bool
    ready: bool
    sms_delivery_ready: bool
    blockers: tuple[str, ...]


def get_sms_marketing_campaign_status() -> SmsMarketingCampaignStatus:
    marketing_enabled = is_feature_enabled(FeatureFlag.ENABLE_SMS_MARKETING_CAMPAIGNS)
    sms_status = get_sms_delivery_status()

    blockers: list[str] = []
    if not marketing_enabled:
        blockers.append("ENABLE_SMS_MARKETING_CAMPAIGNS is false")
    if not sms_status.enabled:
        blockers.append("ENABLE_SMS_DELIVERY is false")
    if marketing_enabled and sms_status.enabled and not sms_status.ready:
        blockers.extend(sms_status.blockers)

    enabled = marketing_enabled and sms_status.enabled
    ready = enabled and not blockers

    return SmsMarketingCampaignStatus(
        enabled=enabled,
        ready=ready,
        sms_delivery_ready=sms_status.ready,
        blockers=tuple(blockers),
    )
