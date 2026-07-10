"""Mailing addresses for dispute letter exports."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.config import Settings, get_settings
from api.core.constants import APP_NAME
from api.modules.accounts.models import Account, AccountBureau

FCRA_CRA_CITATION = "15 U.S.C. § 1681i (FCRA Section 611)"
FCRA_FURNISHER_CITATION = "15 U.S.C. § 1681s-2 (FCRA Section 623)"


@dataclass(frozen=True, slots=True)
class MailingAddress:
    name: str
    lines: tuple[str, ...]

    def formatted_lines(self) -> list[str]:
        return [self.name, *self.lines]


_BUREAU_DISPUTE_ADDRESSES: dict[AccountBureau, MailingAddress] = {
    AccountBureau.EXPERIAN: MailingAddress(
        name="Experian",
        lines=(
            "P.O. Box 4500",
            "Allen, TX 75013",
        ),
    ),
    AccountBureau.EQUIFAX: MailingAddress(
        name="Equifax Information Services LLC",
        lines=(
            "P.O. Box 740256",
            "Atlanta, GA 30374-0256",
        ),
    ),
    AccountBureau.TRANSUNION: MailingAddress(
        name="TransUnion LLC",
        lines=(
            "Consumer Dispute Center",
            "P.O. Box 2000",
            "Chester, PA 19016",
        ),
    ),
}


def bureau_dispute_address(bureau: AccountBureau) -> MailingAddress:
    if bureau in _BUREAU_DISPUTE_ADDRESSES:
        return _BUREAU_DISPUTE_ADDRESSES[bureau]
    bureau_label = bureau.value.replace("_", " ").title()
    return MailingAddress(
        name=f"{bureau_label} Dispute Department",
        lines=("[Verify current CRA dispute mailing address before sending]",),
    )


def furnisher_dispute_address(account: Account) -> MailingAddress:
    furnisher_name = account.original_creditor or account.creditor_name
    return MailingAddress(
        name=f"{furnisher_name} — Dispute Department",
        lines=(
            "[Verify furnisher dispute mailing address before sending]",
            "Use the address on your billing statement or the creditor's website.",
        ),
    )


def resolve_return_address(
    *,
    organization_name: str | None = None,
    settings: Settings | None = None,
) -> MailingAddress:
    config = settings or get_settings()
    name = config.dispute_return_name or organization_name or APP_NAME
    lines = [
        line.strip()
        for line in (
            config.dispute_return_address_line1,
            config.dispute_return_address_line2,
            config.dispute_return_address_line3,
        )
        if line and line.strip()
    ]
    if not lines:
        lines = ["[Add organization return mailing address in deployment settings]"]
    return MailingAddress(name=name, lines=tuple(lines))


def normalize_consumer_address_lines(addresses: list[str]) -> list[str]:
    lines: list[str] = []
    for raw in addresses:
        text = raw.strip()
        if not text:
            continue
        if "\n" in text:
            lines.extend(part.strip() for part in text.splitlines() if part.strip())
            continue
        if "," in text:
            lines.extend(part.strip() for part in text.split(",") if part.strip())
            continue
        lines.append(text)
    return lines


def resolve_consumer_address(
    *,
    consumer_name: str,
    address_lines: list[str] | None = None,
) -> MailingAddress:
    lines = normalize_consumer_address_lines(address_lines or [])
    if not lines:
        lines = ["[Consumer mailing address — use address on government-issued ID]"]
    return MailingAddress(name=consumer_name, lines=tuple(lines))


def has_placeholder_address(address: MailingAddress) -> bool:
    return any(line.startswith("[") for line in address.lines)
