"""Unit tests for checklist markdown export rendering."""

from __future__ import annotations

import uuid

from api.modules.documents.checklist_export import (
    checklist_export_filename,
    render_attorney_checklist_markdown,
    render_cfpb_checklist_markdown,
)
from api.modules.documents.schemas import (
    AccountAttorneyChecklistItem,
    AccountCfpbChecklistItem,
    AttorneyChecklistItem,
    AttorneyChecklistSummary,
    CaseAttorneyChecklistResponse,
    CaseCfpbChecklistResponse,
    CfpbChecklistItem,
    CfpbChecklistSummary,
)


def test_checklist_export_filename() -> None:
    case_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    assert checklist_export_filename("cfpb", case_id) == "cfpb-checklist-12345678.md"
    assert checklist_export_filename("attorney", case_id) == "attorney-checklist-12345678.md"


def test_render_cfpb_checklist_markdown_includes_status_and_disclaimer() -> None:
    case_id = uuid.uuid4()
    checklist = CaseCfpbChecklistResponse(
        case_id=case_id,
        disclaimer="Investigator CFPB escalation checklist only.",
        summary=CfpbChecklistSummary(
            accounts_listed=1,
            required_items=2,
            optional_items=1,
            items_present=1,
            items_missing=1,
            items_unknown=1,
        ),
        accounts=[
            AccountCfpbChecklistItem(
                account_key="capital one:4242",
                creditor_name="Capital One",
                account_number_masked="****4242",
                bureau="experian",
                match_key="capital one:4242",
                top_score=98,
                primary_rule_ids=["cross_bureau.dofd_mismatch"],
                items=[
                    CfpbChecklistItem(
                        item_id="identity_exhibits",
                        category="evidence",
                        title="Include identity exhibits",
                        detail="Government ID and proof of address.",
                        required=True,
                        completion_status="present",
                        completion_source="staff",
                        override_note="Verified ID packet on desk",
                    ),
                    CfpbChecklistItem(
                        item_id="cfpb_narrative",
                        category="filing",
                        title="Draft CFPB narrative",
                        detail="Staff review before submission.",
                        required=True,
                        completion_status="unknown",
                    ),
                ],
            )
        ],
    )
    markdown = render_cfpb_checklist_markdown(checklist)
    assert "# CFPB escalation checklist" in markdown
    assert "Investigator CFPB escalation checklist only." in markdown
    assert "Capital One" in markdown
    assert "**present**" in markdown
    assert "(staff)" in markdown
    assert "Staff note: Verified ID packet on desk" in markdown
    assert "**unknown**" in markdown
    assert "Staff-mediated export only" in markdown
    assert "Does not file with CFPB" in markdown


def test_render_attorney_checklist_markdown_includes_escalation() -> None:
    case_id = uuid.uuid4()
    checklist = CaseAttorneyChecklistResponse(
        case_id=case_id,
        disclaimer="Investigator attorney-preserve packet checklist only.",
        summary=AttorneyChecklistSummary(
            accounts_listed=1,
            required_items=1,
            optional_items=0,
            escalation_flagged=1,
            items_present=1,
            items_missing=0,
            items_unknown=0,
        ),
        accounts=[
            AccountAttorneyChecklistItem(
                account_key="capital one:4242",
                creditor_name="Capital One",
                account_number_masked="****4242",
                bureau=None,
                match_key="capital one:4242",
                top_score=98,
                primary_rule_ids=["cross_bureau.dofd_mismatch"],
                attorney_escalation=True,
                items=[
                    AttorneyChecklistItem(
                        item_id="attorney_handoff_narrative",
                        category="filing",
                        title="Draft attorney handoff narrative",
                        detail="Staff must review before sharing.",
                        required=True,
                        completion_status="unknown",
                    )
                ],
            )
        ],
    )
    markdown = render_attorney_checklist_markdown(checklist)
    assert "# Attorney-preserve checklist" in markdown
    assert "Escalation: yes" in markdown
    assert "Escalation-flagged: 1" in markdown
    assert "Draft attorney handoff narrative" in markdown


def test_render_empty_checklist_still_returns_markdown() -> None:
    case_id = uuid.uuid4()
    checklist = CaseCfpbChecklistResponse(
        case_id=case_id,
        disclaimer="Investigator CFPB escalation checklist only.",
        summary=CfpbChecklistSummary(
            accounts_listed=0,
            required_items=0,
            optional_items=0,
        ),
        accounts=[],
    )
    markdown = render_cfpb_checklist_markdown(checklist)
    assert "No accounts listed for CFPB escalation." in markdown
    assert "Staff-mediated export only" in markdown
