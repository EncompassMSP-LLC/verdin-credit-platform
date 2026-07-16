# Version 5.21 Scope & Deferrals

Formal scope for **Version 5.21 — Reinvestigation Analytics & Evidence Polish (Compliance Intelligence Phase 14)**. Builds on shipped **v5.20.0** Reinvestigation Analytics & Evidence Refinement (Phase 13).

**Kickoff date:** 2026-07-16  
**Target:** Polish the analytics and evidence surfaces shipped in 5.20 by closing their documented limitations — add a single-call per-recipient (bureau vs furnisher) breakdown to reinvestigation outcome analytics, compare `high_balance` and `credit_limit` in cross-bureau discrepancy detection, and upgrade the litigation evidence PDF from a plain wrapped-text canvas to a structured multi-section layout — **without** any live bureau response polling, automated re-dispute filing, unsupervised escalation, automated litigation filing, or cross-tenant benchmarks.

## Theme

5.20 shipped `group_by=bureau` analytics, per-recipient §611 extended-window accuracy, PDF litigation export, and a $1.00 cross-bureau monetary tolerance with past-due / date-reported fields. Documented leftovers remain: only `bureau` is a supported `group_by` dimension; high-balance and credit-limit are still unused in cross-bureau comparison; and the PDF export is a simple wrapped-text canvas without section structure. Phase 14 closes those gaps — all as read-only, computed polish over data the platform already stores.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants. Litigation-readiness exports assemble evidence for a person to review and file — the platform never transmits anything to a court, bureau, or attorney.

## Epic outcomes (target)

| Epic | Theme                                    | 5.21 target | Summary                                                                                 |
| ---- | ---------------------------------------- | ----------- | --------------------------------------------------------------------------------------- |
| 1    | Per-recipient analytics breakdown        | Released    | Single-call `group_by=recipient` roll-up on the reinvestigation outcome analytics model |
| 2    | Cross-bureau high_balance / credit_limit | Released    | Compare high balance and credit limit across sibling bureaus in litigation evidence     |
| 3    | Structured PDF litigation export layout  | Released    | Multi-section reportlab layout for the operator-gated litigation evidence PDF           |
| 4    | Capability matrix / governance sign-off  | Released    | Scope, checklist, matrix rows, release notes                                            |

## Shipped from 5.20 (foundation — do not regress)

All v5.20.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — per-bureau analytics breakdown, per-recipient extended-window accuracy, PDF litigation evidence export, and cross-bureau discrepancy depth ($1.00 tolerance + past-due / date-reported). See [`version-5.20-scope.md`](version-5.20-scope.md).

## Explicit deferrals (not 5.21)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.22+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing                     | 5.22+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 5.22+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-configurable cross-bureau balance tolerance | 5.22+       | Needs org-settings product decision; module constant remains   |

## Partial capability limits (5.21 targets)

### Per-recipient analytics breakdown (Planned)

**Included:** An optional `group_by=recipient` roll-up on `GET /reporting/reinvestigation-outcomes` so operators can compare credit-bureau vs furnisher response outcomes in one call; attributed via the response's linked dispute letter `recipient_type` (unlinked responses land under `unknown`). Existing `group_by=bureau`, filters, and top-level aggregate remain unchanged.

**Not included:** Cross-tenant comparisons; any benchmark against other organizations' data.

### Cross-bureau high_balance / credit_limit (Planned)

**Included:** Compare stored `high_balance` and `credit_limit` across sibling bureaus using the same $1.00 monetary tolerance as balance/past-due; new discrepancy kinds `high_balance_conflict` and `credit_limit_conflict` surfaced in the litigation packet.

**Not included:** New bureau data collection; org-configurable tolerance; any live comparison beyond stored parsed reports.

### Structured PDF litigation export layout (Planned)

**Included:** Upgrade `format=pdf` on the litigation evidence export to a structured multi-section reportlab layout (clear headings, spaced sections, consistent typography) while keeping the same content and disclaimer as the text export.

**Not included:** Auto-generating legal pleadings, branding/templates per org, auto-filing, or transmitting the export without a human action.

## Related documents

- [Version 5.21 completion checklist](../development/version-5.21-completion-checklist.md)
- [Version 5.20 scope](version-5.20-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
