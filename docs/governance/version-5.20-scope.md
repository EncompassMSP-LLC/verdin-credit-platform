# Version 5.20 Scope & Deferrals

Formal scope for **Version 5.20 — Reinvestigation Analytics & Evidence Refinement (Compliance Intelligence Phase 13)**. Builds on shipped **v5.19.0** Reinvestigation Analytics & Evidence Depth (Phase 12).

**Kickoff date:** 2026-07-15  
**Target:** Refine the analytics and evidence surfaces shipped in 5.19 by closing their documented limitations — add a single-call per-bureau breakdown to reinvestigation outcome analytics, compute the §611 extended-window flag per recipient, add a PDF format to the operator-gated litigation evidence export, and give cross-bureau discrepancy detection a balance tolerance band plus additional compared fields — **without** any live bureau response polling, automated re-dispute filing, unsupervised escalation, automated litigation filing, or cross-tenant benchmarks.

## Theme

5.19 shipped date-range/bureau analytics slicing, per-recipient §611 clock splits, cross-bureau litigation evidence, and an operator-gated text evidence export. Each carried documented tech debt: outcome analytics only filter one bureau at a time (no single-call breakdown); the clock's `extended` 45-day flag is computed once per tradeline and applied to every recipient sub-clock rather than per recipient; the litigation export is text-only (no PDF); and cross-bureau balance conflicts flag any difference with no tolerance band. Phase 13 closes those gaps — all as read-only, computed refinement over data the platform already stores.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants. Litigation-readiness exports assemble evidence for a person to review and file — the platform never transmits anything to a court, bureau, or attorney.

## Epic outcomes (target)

| Epic | Theme                                   | 5.20 target | Summary                                                                            |
| ---- | --------------------------------------- | ----------- | ---------------------------------------------------------------------------------- |
| 1    | Per-bureau analytics breakdown          | Planned     | Single-call per-bureau roll-up on the reinvestigation outcome analytics read model |
| 2    | Per-recipient extended-window accuracy  | Planned     | Compute the §611(a)(1)(B) 45-day flag per recipient sub-clock, not per tradeline   |
| 3    | PDF litigation evidence export          | Planned     | Add a `pdf` format to the operator-gated litigation evidence export                |
| 4    | Cross-bureau discrepancy depth          | Planned     | Balance tolerance band + additional compared fields in cross-bureau evidence       |
| 5    | Capability matrix / governance sign-off | Planned     | Scope, checklist, matrix rows, release notes                                       |

## Shipped from 5.19 (foundation — do not regress)

All v5.19.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — date-range/bureau reinvestigation analytics slicing, per-recipient §611 clock splits, litigation-packet cross-bureau evidence, and the operator-gated text litigation evidence export. See [`version-5.19-scope.md`](version-5.19-scope.md).

## Explicit deferrals (not 5.20)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.21+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing                     | 5.21+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 5.21+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |

## Partial capability limits (5.20 targets)

### Per-bureau analytics breakdown (Planned)

**Included:** An optional single-call per-bureau roll-up on `GET /reporting/reinvestigation-outcomes` (e.g. `group_by=bureau`) so operators can compare all bureaus in one response instead of one filtered call per bureau; the existing single-bureau filter and top-level aggregate remain unchanged.

**Not included:** Cross-tenant comparisons; any benchmark against other organizations' data.

### Per-recipient extended-window accuracy (Planned)

**Included:** Compute the §611(a)(1)(B) 45-day extended-window flag independently for each recipient sub-clock (based on documents supplied within that recipient's window) rather than applying one tradeline-level flag to every recipient.

**Not included:** Any change to how documents are uploaded or linked; no new document collection.

### PDF litigation evidence export (Planned)

**Included:** A `pdf` format on the operator-gated litigation evidence export, reusing the existing dispute-letter reportlab pipeline; text remains the default. Same write-permission gate and disclaimer.

**Not included:** Auto-generating legal pleadings, auto-filing, or transmitting the export to a court, bureau, or attorney without a human action.

### Cross-bureau discrepancy depth (Planned)

**Included:** A configurable balance tolerance band so trivial balance differences no longer flag as conflicts, plus additional compared fields (e.g. `date_reported`, `past_due_amount`) in cross-bureau discrepancy detection; surfaced in the litigation packet's cross-bureau evidence.

**Not included:** New bureau data collection; any live comparison beyond stored parsed reports.

## Related documents

- [Version 5.20 completion checklist](../development/version-5.20-completion-checklist.md)
- [Version 5.19 scope](version-5.19-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
