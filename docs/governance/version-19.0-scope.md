# Version 19.0 Scope & Deferrals

Formal scope for **Version 19.0 — Reinvestigation Benchmark Depth (Compliance Intelligence Phase 18)**. Builds on shipped **v18.0.0** Reinvestigation Operations Polish (Phase 17).

**Kickoff date:** 2026-07-16  
**Target:** Deepen org-internal outcome benchmarks — optional per-bureau window defaults on dispute settings, and a single-call per-bureau breakdown on the Outcome benchmarks API/UI — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

18.0 added org-wide benchmark window defaults and ingestion case/account scope, but Reporting Center still uses one window pair for every bureau filter, and comparing Equifax / Experian / TransUnion benchmarks requires multiple round-trips. Phase 18 is non-blocked depth over configuration and analytics the platform already owns.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                   | 19.0 target | Summary                                                                                          |
| ---- | --------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------ |
| 1    | Per-bureau benchmark window defaults    | Planned     | Optional Equifax/Experian/TransUnion window overrides on dispute settings; fall back to org pair |
| 2    | Outcome benchmarks per-bureau breakdown | Planned     | `group_by=bureau` on benchmarks API + Reporting Center per-bureau rates table                    |
| 3    | Capability matrix / governance sign-off | Planned     | Scope, checklist, matrix rows, release notes                                                     |

## Shipped from 18.0 (foundation — do not regress)

All v18.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — org dispute settings (tolerance + org-wide benchmark windows), Reporting Center Outcome benchmarks tab, and Compliance Center Response ingestion with case/account scope. See [`version-18.0-scope.md`](version-18.0-scope.md).

## Explicit deferrals (not 19.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 20.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 20.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 20.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead          | 20.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs    | 20.0+       | Staff on-demand read models are sufficient                     |

## Partial capability limits (19.0 targets)

### Per-bureau benchmark window defaults (Planned)

**Included:** Optional per-bureau `baseline_days` / `recent_days` overrides (Equifax / Experian / TransUnion) on organization dispute settings; resolve when Reporting requests a bureau filter; Org Admin UI to edit overrides; fall back to org-wide pair then platform defaults (90/30).

**Not included:** Per-recipient windows; automatic scheduled recompute jobs; cross-tenant baselines.

### Outcome benchmarks per-bureau breakdown (Planned)

**Included:** Optional `group_by=bureau` on `GET /reporting/reinvestigation-outcomes/benchmarks` returning per-bureau baseline/recent analytics and advisory rate deltas; Reporting Center always requests the breakdown and renders a per-bureau table under the org aggregate.

**Not included:** Cross-tenant percentile ranks; editing historical responses from the panel; exporting benchmark PII.

## Related documents

- [Version 19.0 completion checklist](../development/version-19.0-completion-checklist.md)
- [Version 18.0 scope](version-18.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
