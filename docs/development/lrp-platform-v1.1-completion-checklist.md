# LRP Platform V1.1 Completion Checklist

Post–V1.0 product depth on the shared monorepo (edition, not fork). Continue the sprint loop: sync `main` → one slice → verify → PR → auto-merge → next.

**Prior release:** [`lrp-platform-v1.0.0`](../release-notes/lrp-platform-v1.0.0.md) · Hardening: [`lrp-v1.0-post-release-hardening.md`](lrp-v1.0-post-release-hardening.md)

## Ordered slices

| Order | ID       | Slice                                                       | Status |
| ----- | -------- | ----------------------------------------------------------- | ------ |
| 1     | LRP-208A | Evidence vault document↔issue association                   | ✅     |
| 2     | LRP-208B | Case action timeline panel (reuse `GET /timeline?case_id=`) | ☐      |
| 3     | LRP-209A | Unwanted-call complaint workflow + follow-up tracking       | ☐      |

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
