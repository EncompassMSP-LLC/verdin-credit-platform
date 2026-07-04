"""SMS marketing campaign delivery worker readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.sms_marketing import get_sms_marketing_campaign_status


@dataclass(frozen=True)
class SmsMarketingDeliveryStatus:
    enabled: bool
    ready: bool
    campaign_ready: bool
    blockers: tuple[str, ...]


def is_sms_marketing_delivery_enabled() -> bool:
    return is_feature_enabled(FeatureFlag.ENABLE_SMS_MARKETING_DELIVERY)


def get_sms_marketing_delivery_status() -> SmsMarketingDeliveryStatus:
    campaign_status = get_sms_marketing_campaign_status()
    delivery_enabled = is_sms_marketing_delivery_enabled()

    blockers: list[str] = []
    if not delivery_enabled:
        blockers.append("ENABLE_SMS_MARKETING_DELIVERY is false")
    if delivery_enabled and not campaign_status.ready:
        blockers.extend(campaign_status.blockers)

    enabled = delivery_enabled and campaign_status.enabled
    return SmsMarketingDeliveryStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        campaign_ready=campaign_status.ready,
        blockers=tuple(blockers),
    )
