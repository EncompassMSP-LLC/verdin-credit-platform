"""Render dispute-strategy checklist packets as staff-mediated markdown exports."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal

_FOOTER = (
    "---\n"
    "Staff-mediated export only. Does not file with CFPB, transmit to counsel, "
    "or attach exhibits. Use mail-packet / report-excerpt downloads for evidence.\n"
)

_CATEGORY_ORDER: tuple[str, ...] = ("correspondence", "evidence", "chronology", "filing")


def checklist_export_filename(kind: Literal["cfpb", "attorney"], case_id: uuid.UUID) -> str:
    short = str(case_id).replace("-", "")[:8]
    return f"{kind}-checklist-{short}.md"


def _item_line(item: Any) -> str:
    required = "required" if bool(getattr(item, "required", False)) else "optional"
    status = getattr(item, "completion_status", None) or "unknown"
    source = getattr(item, "completion_source", None) or "computed"
    staff_suffix = " (staff)" if source == "staff" else ""
    title = getattr(item, "title", "") or ""
    detail = getattr(item, "detail", "") or ""
    lines = [f"- [{required}] **{status}**{staff_suffix} — {title}"]
    if detail:
        lines.append(f"  - {detail}")
    return "\n".join(lines)


def _render_account_section(account: Any, *, include_escalation: bool) -> str:
    creditor = getattr(account, "creditor_name", None) or "Unknown creditor"
    masked = getattr(account, "account_number_masked", None)
    title = f"{creditor}" + (f" · {masked}" if masked else "")
    score = getattr(account, "top_score", 0)
    lines = [
        f"## Account: {title} (top {score}/100)",
        f"- Key: `{getattr(account, 'account_key', '')}`",
        f"- Bureau: {getattr(account, 'bureau', None) or '—'}",
        f"- Match key: {getattr(account, 'match_key', None) or '—'}",
    ]
    rules = list(getattr(account, "primary_rule_ids", []) or [])
    lines.append(f"- Rules: {', '.join(f'`{rule}`' for rule in rules) if rules else '—'}")
    if include_escalation:
        flagged = bool(getattr(account, "attorney_escalation", False))
        lines.append(f"- Escalation: {'yes' if flagged else 'no'}")
    lines.append("")

    items: Sequence[Any] = tuple(getattr(account, "items", ()) or ())
    by_category: dict[str, list[Any]] = {category: [] for category in _CATEGORY_ORDER}
    for item in items:
        category = getattr(item, "category", "filing")
        by_category.setdefault(category, []).append(item)

    for category in _CATEGORY_ORDER:
        category_items = by_category.get(category) or []
        if not category_items:
            continue
        lines.append(f"### {category.title()}")
        for item in category_items:
            lines.append(_item_line(item))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_summary(summary: Any, *, include_escalation: bool) -> list[str]:
    lines = [
        "## Summary",
        f"- Accounts listed: {getattr(summary, 'accounts_listed', 0)}",
        (
            f"- Required / optional: {getattr(summary, 'required_items', 0)} / "
            f"{getattr(summary, 'optional_items', 0)}"
        ),
        (
            f"- Present / missing / unknown: {getattr(summary, 'items_present', 0)} / "
            f"{getattr(summary, 'items_missing', 0)} / {getattr(summary, 'items_unknown', 0)}"
        ),
    ]
    if include_escalation:
        lines.append(f"- Escalation-flagged: {getattr(summary, 'escalation_flagged', 0)}")
    lines.append("")
    return lines


def render_cfpb_checklist_markdown(checklist: Any) -> str:
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# CFPB escalation checklist",
        f"Case ID: {getattr(checklist, 'case_id', '')}",
        f"Generated: {generated}",
        "",
        f"> {getattr(checklist, 'disclaimer', '')}",
        "",
    ]
    lines.extend(_render_summary(getattr(checklist, "summary", None), include_escalation=False))
    accounts = list(getattr(checklist, "accounts", []) or [])
    if not accounts:
        lines.append("No accounts listed for CFPB escalation.")
        lines.append("")
    else:
        for account in accounts:
            lines.append(_render_account_section(account, include_escalation=False))
    lines.append(_FOOTER)
    return "\n".join(lines)


def render_attorney_checklist_markdown(checklist: Any) -> str:
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Attorney-preserve checklist",
        f"Case ID: {getattr(checklist, 'case_id', '')}",
        f"Generated: {generated}",
        "",
        f"> {getattr(checklist, 'disclaimer', '')}",
        "",
    ]
    lines.extend(_render_summary(getattr(checklist, "summary", None), include_escalation=True))
    accounts = list(getattr(checklist, "accounts", []) or [])
    if not accounts:
        lines.append("No accounts listed for attorney preserve.")
        lines.append("")
    else:
        for account in accounts:
            lines.append(_render_account_section(account, include_escalation=True))
    lines.append(_FOOTER)
    return "\n".join(lines)
