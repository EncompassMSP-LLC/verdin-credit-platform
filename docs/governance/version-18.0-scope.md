# Version 18.0 Scope & Deferrals

Formal scope for **Version 18.0 — Reinvestigation Operations Polish (Compliance Intelligence Phase 17)**. Builds on shipped **v17.0.0** Reinvestigation Operations Surfaces (Phase 16).

**Kickoff date:** 2026-07-16  
**Target:** Close operator polish gaps left by 16.0/17.0 — org-configurable default windows for org-internal outcome benchmarks, and case/account scoping on the Compliance Center ingestion audit UI — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

17.0 surfaced Phase 15 APIs in staff UI, but benchmark windows remain hard-coded defaults (90/30) and ingestion audit starts cannot be scoped to a case or account from the UI even though the API accepts those fields. Phase 17 is non-blocked polish over configuration and staff surfaces the platform already owns.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                      | 18.0 target | Summary                                                                                      |
| ---- | ------------------------------------------ | ----------- | -------------------------------------------------------------------------------------------- |
| 1    | Org-configurable benchmark window defaults | Planned     | Per-org `baseline_days` / `recent_days` on dispute settings; Reporting UI reads org defaults |
| 2    | Ingestion audit case/account scope UI      | Planned     | Compliance Center filters + start form accept optional case_id / account_id                  |
| 3    | Capability matrix / governance sign-off    | Planned     | Scope, checklist, matrix rows, release notes                                                 |

## Shipped from 17.0 (foundation — do not regress)

All v17.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — Reporting Center Outcome benchmarks tab and Compliance Center Response ingestion tab. See [`version-17.0-scope.md`](version-17.0-scope.md).

## Explicit deferrals (not 18.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 19.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 19.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 19.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead          | 19.0+       | Branding / template product decision                           |

## Partial capability limits (18.0 targets)

### Org-configurable benchmark window defaults (Planned)

**Included:** Persist per-org `reinvestigation_benchmark_baseline_days` (default 90) and `reinvestigation_benchmark_recent_days` (default 30) on organization dispute settings; expose via org-admin GET/PATCH; Reporting Center Outcome benchmarks tab initializes filters from org defaults.

**Not included:** Per-bureau default windows; automatic scheduled recompute jobs; cross-tenant baselines.

### Ingestion audit case/account scope UI (Planned)

**Included:** Optional case_id / account_id on Compliance Center start form and list filters (API already supports these fields).

**Not included:** Live polling, webhook receivers, or auto-recording bureau responses without staff review.

## Related documents

- [Version 18.0 completion checklist](../development/version-18.0-completion-checklist.md)
- [Version 17.0 scope](version-17.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
