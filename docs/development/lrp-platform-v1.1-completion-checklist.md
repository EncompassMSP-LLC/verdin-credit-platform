# LRP Platform V1.1 Completion Checklist

Post–V1.0 product depth on the shared monorepo (edition, not fork). Continue the sprint loop: sync `main` → one slice → verify → PR → auto-merge → next.

**Prior release:** [`lrp-platform-v1.0.0`](../release-notes/lrp-platform-v1.0.0.md) · Hardening: [`lrp-v1.0-post-release-hardening.md`](lrp-v1.0-post-release-hardening.md)

**Release:** [`lrp-platform-v1.1.0`](../release-notes/lrp-platform-v1.1.0.md) · Tag / GitHub Release: `lrp-platform-v1.1.0`  
**Commit SHA:** `850e0430b34482abf0225833d38446a4fa938faf`  
**Status:** **Formally released** (2026-07-30)

## Exit criteria for "LRP Platform V1.1 done"

- [x] Ordered slices LRP-208A → LRP-208B → LRP-209A merged to `main`
- [x] Capability matrix + API reference updated for V1.1 surfaces
- [x] No automatic complaint submission; eligibility remains advisory
- [x] Migrations `115_issue_evidence_links` + `116_unwanted_call_incidents` on `main`
- [x] Release notes + tag `lrp-platform-v1.1.0` + recorded commit SHA
- [x] Smoke validation (API slice tests + CI green on #414–#417)
- [x] Roadmap / changelog / product backlog updated; deferred timeline items as PB-011/PB-012

Deferred timeline lifecycle emits (draft workflow, delivery confirmation, issue detected/resolved) stay **out of scope** unless a real operator workflow gap appears.

## Ordered slices

| Order | ID       | Slice                                                       | Status | PR   |
| ----- | -------- | ----------------------------------------------------------- | ------ | ---- |
| 1     | LRP-208A | Evidence vault document↔issue association                   | ✅     | #414 |
| 2     | LRP-208B | Case action timeline panel (reuse `GET /timeline?case_id=`) | ✅     | #415 |
| 3     | LRP-209A | Unwanted-call complaint workflow + follow-up tracking       | ✅     | #416 |
| —     | Closeout | Release notes + tag `lrp-platform-v1.1.0`                   | ✅     | —    |

## Ranking notes

1. **LRP-208A first** — unblocks explainability cards / letter drafts with real attached vault docs; clearest missing V1.0 depth.
2. **LRP-208B** — embed existing timeline feed on Case Detail + CRM; optional `ISSUE_EVIDENCE_LINKED` event after associations ship.
3. **LRP-209A** — builds on LRP-209 prefs / DNC assistance; complaint + follow-up tracking without silent third-party registration.

## Slice notes

### LRP-208A — Issue evidence vault links

- Migration `115_issue_evidence_links`; model `IssueEvidenceLink`
- `GET/POST/DELETE /cases/{id}/issue-evidence-links`; explainability cards include `associated_documents`
- CRO + CRM panels: link/unlink case vault documents by `source_id`
- Staff-mediated only; never auto-files or transmits

### LRP-208B — Case action timeline panel

- Reuses append-only `timeline_events` (no new table)
- Emits `ISSUE_EVIDENCE_LINKED` / `ISSUE_EVIDENCE_REMOVED` with `source_id` + source-record metadata
- `GET /timeline?source_id=` JSONB filter for issue-scoped views
- CRO `CaseActionTimelinePanel` + CRM Activity panel: newest/oldest, issue filter, document/issue deep links
- Deferred lifecycle emits (letter draft workflow, delivery confirmation, issue detected/resolved): track for follow-up slices; existing CASE_/DOCUMENT_/DISPUTE_LETTER_/TASK_ events already appear on the case feed

### LRP-209A — Unwanted-call complaint workflow

- Migration `116_unwanted_call_incidents`; model `UnwantedCallIncident`
- `GET/POST/PATCH/DELETE /clients/{id}/unwanted-call-incidents` with preference snapshot + advisory eligibility + staff-gated draft text
- Timeline emits `UNWANTED_CALL_INCIDENT_RECORDED` / `UNWANTED_CALL_INCIDENT_UPDATED`
- CRM panel next to communication preferences; never auto-submits to FTC/CFPB/DNC
- Explicit non-goals: silent registry registration, liability conclusions, auto-transmit letters

## Closeout — Release notes + tag (2026-07-30)

- Release notes: [`docs/release-notes/lrp-platform-v1.1.0.md`](../release-notes/lrp-platform-v1.1.0.md)
- Git tag / GitHub Release: `lrp-platform-v1.1.0`
- Commit SHA: `850e0430b34482abf0225833d38446a4fa938faf`
- Ordered backlog `208A → 208B → 209A` complete; deferred timeline enrichments → PB-011 / PB-012
- Formal status: **released**
