# Version 5.19 Scope & Deferrals

Formal scope for **Version 5.19 — Reinvestigation Analytics & Evidence Depth (Compliance Intelligence Phase 12)**. Builds on shipped **v5.18.0** Reinvestigation Depth & Litigation Readiness (Phase 11).

**Kickoff date:** 2026-07-15  
**Target:** Deepen the analytics and evidence surfaces shipped in 5.18 — add date-range and per-bureau slicing to reinvestigation outcome analytics, split the §611 clock and round counts by recipient (bureau vs furnisher), enrich the litigation-readiness packet with cross-bureau discrepancy evidence, and add an operator-gated evidence export — **without** any live bureau response polling, automated re-dispute filing, unsupervised escalation, automated litigation filing, or cross-tenant benchmarks.

## Theme

5.18 shipped per-letter multi-round §611 clocks, the extended 45-day window, per-org outcome analytics, and an operator-gated litigation-readiness packet. Several documented limitations remain: outcome analytics cover all-time data with no date-range or per-bureau slicing; `dispute_round_count` counts sent letters regardless of recipient; and the litigation packet does not yet incorporate cross-bureau discrepancy evidence or produce an exportable document. Phase 12 closes those gaps — all as read-only, computed depth over data the platform already stores.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants. Litigation-readiness exports assemble evidence for a person to review and file — the platform never transmits anything to a court, bureau, or attorney.

## Epic outcomes (target)

| Epic | Theme                                      | 5.19 target | Summary                                                                            |
| ---- | ------------------------------------------ | ----------- | ---------------------------------------------------------------------------------- |
| 1    | Reinvestigation analytics slicing          | Planned     | Date-range + per-bureau filters on the per-org outcome analytics read model        |
| 2    | Per-recipient reinvestigation clock splits | Planned     | Split §611 clock start / round counts by recipient (bureau vs furnisher)           |
| 3    | Litigation packet cross-bureau evidence    | Planned     | Fold cross-bureau discrepancy signals into the willful-noncompliance assessment    |
| 4    | Operator-gated litigation evidence export  | Planned     | Downloadable evidence document (text) for attorney handoff; never auto-transmitted |
| 5    | Capability matrix / governance sign-off    | Planned     | Scope, checklist, matrix rows, release notes                                       |

## Shipped from 5.18 (foundation — do not regress)

All v5.18.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — the `sent_at`-keyed multi-round §611 clock, the extended 45-day reinvestigation window, per-org reinvestigation outcome analytics, and the operator-gated litigation-readiness evidence packet. See [`version-5.18-scope.md`](version-5.18-scope.md).

## Explicit deferrals (not 5.19)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.20+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing                     | 5.20+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 5.20+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |

## Partial capability limits (5.19 targets)

### Reinvestigation analytics slicing (Planned)

**Included:** Optional `start`/`end` date-range and `bureau` filters on `GET /reporting/reinvestigation-outcomes`, applied over recorded responses; the read model reports the applied filters back.

**Not included:** Cross-tenant comparisons; any benchmark against other organizations' data.

### Per-recipient reinvestigation clock splits (Planned)

**Included:** Track the §611 clock start and round count per recipient (credit bureau vs furnisher) so a tradeline disputed with both carries independent deadlines; surface the split in the clock read model.

**Not included:** Any change to how disputes are sent or to recipient selection.

### Litigation packet cross-bureau evidence (Planned)

**Included:** Incorporate existing cross-bureau discrepancy signals into the litigation-readiness assessment as additional willful-noncompliance indicators (e.g. an item verified by one bureau while inconsistent across bureaus).

**Not included:** New bureau data collection; any live comparison beyond stored parsed reports.

### Operator-gated litigation evidence export (Planned)

**Included:** A downloadable, human-readable evidence document (text) assembled from the litigation packet, gated to write-permission operators, for attorney handoff; mirrors the existing dispute-letter export pipeline.

**Not included:** Auto-generating legal pleadings, auto-filing, or transmitting the export to a court, bureau, or attorney without a human action.

## Related documents

- [Version 5.19 completion checklist](../development/version-5.19-completion-checklist.md)
- [Version 5.18 scope](version-5.18-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
