"""Cross-bureau discrepancy detection for litigation evidence (Phase 12 / 13).

Pure, side-effect-free comparison of a tradeline against its same-creditor
siblings reported to *other* credit bureaus. A single furnisher item reported
inconsistently across bureaus — deleted at one but verified at another, or with
divergent balances/statuses — is a classic FCRA reinvestigation-failure signal
(the item cannot be simultaneously accurate everywhere).

Guardrails: this only compares data already stored on the platform. It never
contacts a bureau, never files anything, and never drafts a legal pleading. The
findings are advisory evidence a human attorney reviews.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

CrossBureauKind = Literal[
    "outcome_conflict",
    "dispute_status_conflict",
    "balance_conflict",
    "account_status_conflict",
    "payment_status_conflict",
    "past_due_conflict",
    "date_reported_conflict",
]

# Outcomes that mean the item was removed/fixed at that bureau.
_FAVORABLE_OUTCOMES = frozenset({"deleted", "corrected"})
# Outcomes that mean the item survived the dispute at that bureau.
_ADVERSE_OUTCOMES = frozenset({"verified", "rejected"})

# Trivial balance / past-due differences at or below this amount do not flag.
DEFAULT_BALANCE_TOLERANCE = Decimal("1.00")


@dataclass(frozen=True)
class BureauTradelineView:
    """A single bureau's view of a tradeline, reduced for comparison."""

    account_id: object
    bureau: str
    latest_outcome: str | None
    dispute_status: str | None
    account_status: str | None
    payment_status: str | None
    balance: Decimal | None
    past_due_amount: Decimal | None = None
    date_reported: date | None = None


@dataclass(frozen=True)
class CrossBureauDiscrepancy:
    """One discrepancy between the target tradeline and a sibling bureau."""

    kind: CrossBureauKind
    bureau: str
    detail: str


@dataclass(frozen=True)
class CrossBureauEvidence:
    """The cross-bureau comparison result for one target tradeline."""

    compared_bureaus: list[str] = field(default_factory=list)
    discrepancies: list[CrossBureauDiscrepancy] = field(default_factory=list)

    @property
    def conflict_count(self) -> int:
        return len(self.discrepancies)

    @property
    def has_outcome_conflict(self) -> bool:
        return any(d.kind == "outcome_conflict" for d in self.discrepancies)


def _normalize(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip().lower()
    return stripped or None


def _exceeds_tolerance(
    left: Decimal | None,
    right: Decimal | None,
    *,
    tolerance: Decimal,
) -> bool:
    """True when both amounts are present and their absolute difference exceeds tolerance."""
    if left is None or right is None:
        return False
    return abs(left - right) > tolerance


def detect_cross_bureau_discrepancies(
    target: BureauTradelineView,
    siblings: list[BureauTradelineView],
    *,
    balance_tolerance: Decimal = DEFAULT_BALANCE_TOLERANCE,
) -> CrossBureauEvidence:
    """Compare ``target`` to same-creditor tradelines at other bureaus.

    ``siblings`` should already be filtered to the same normalized creditor and
    exclude the target account. Returns the set of bureaus compared and the
    discrepancies found. The strongest signal is an ``outcome_conflict``: the
    item was deleted/corrected at one bureau but verified/rejected at another.

    Balance and past-due differences at or below ``balance_tolerance`` (default
    $1.00) are treated as rounding noise and do not flag a conflict.
    """
    discrepancies: list[CrossBureauDiscrepancy] = []
    compared: list[str] = []

    target_outcome = _normalize(target.latest_outcome)
    target_status = _normalize(target.dispute_status)
    target_acct_status = _normalize(target.account_status)
    target_pay_status = _normalize(target.payment_status)

    for sibling in siblings:
        compared.append(sibling.bureau)
        sib_outcome = _normalize(sibling.latest_outcome)

        if (target_outcome in _ADVERSE_OUTCOMES and sib_outcome in _FAVORABLE_OUTCOMES) or (
            target_outcome in _FAVORABLE_OUTCOMES and sib_outcome in _ADVERSE_OUTCOMES
        ):
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="outcome_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"This bureau's outcome ({target_outcome}) conflicts with "
                        f"{sibling.bureau}'s outcome ({sib_outcome}) for the same tradeline — "
                        "the item cannot be simultaneously accurate and inaccurate."
                    ),
                )
            )

        sib_status = _normalize(sibling.dispute_status)
        if target_status is not None and sib_status is not None and target_status != sib_status:
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="dispute_status_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"Dispute status differs across bureaus: {target_status} here vs "
                        f"{sib_status} at {sibling.bureau}."
                    ),
                )
            )

        sib_acct_status = _normalize(sibling.account_status)
        if (
            target_acct_status is not None
            and sib_acct_status is not None
            and target_acct_status != sib_acct_status
        ):
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="account_status_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"Account status differs across bureaus: {target_acct_status} here vs "
                        f"{sib_acct_status} at {sibling.bureau}."
                    ),
                )
            )

        sib_pay_status = _normalize(sibling.payment_status)
        if (
            target_pay_status is not None
            and sib_pay_status is not None
            and target_pay_status != sib_pay_status
        ):
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="payment_status_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"Payment status differs across bureaus: {target_pay_status} here vs "
                        f"{sib_pay_status} at {sibling.bureau}."
                    ),
                )
            )

        if _exceeds_tolerance(target.balance, sibling.balance, tolerance=balance_tolerance):
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="balance_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"Reported balance differs across bureaus: {target.balance} here vs "
                        f"{sibling.balance} at {sibling.bureau} "
                        f"(tolerance ${balance_tolerance})."
                    ),
                )
            )

        if _exceeds_tolerance(
            target.past_due_amount, sibling.past_due_amount, tolerance=balance_tolerance
        ):
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="past_due_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"Past-due amount differs across bureaus: {target.past_due_amount} here vs "
                        f"{sibling.past_due_amount} at {sibling.bureau} "
                        f"(tolerance ${balance_tolerance})."
                    ),
                )
            )

        if (
            target.date_reported is not None
            and sibling.date_reported is not None
            and target.date_reported != sibling.date_reported
        ):
            discrepancies.append(
                CrossBureauDiscrepancy(
                    kind="date_reported_conflict",
                    bureau=sibling.bureau,
                    detail=(
                        f"Date reported differs across bureaus: {target.date_reported} here vs "
                        f"{sibling.date_reported} at {sibling.bureau}."
                    ),
                )
            )

    return CrossBureauEvidence(compared_bureaus=compared, discrepancies=discrepancies)
