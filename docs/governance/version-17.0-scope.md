# Version 17.0 Scope & Deferrals

Formal scope for **Version 17.0 — Reinvestigation Operations Surfaces (Compliance Intelligence Phase 16)**. Builds on shipped **v16.0.0** Reinvestigation Operations & Configuration (Phase 15).

**Kickoff date:** 2026-07-16  
**Target:** Surface the Phase 15 operator APIs in staff UI — Reporting Center org-internal benchmarks and Compliance Center bureau response ingestion audit — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

16.0 shipped org-configurable cross-bureau tolerance (with Org Admin UI), a bureau response ingestion audit API (no frontend), and org-internal reinvestigation outcome benchmarks (no frontend). Phase 16 closes those operator-surface gaps so staff can use the scaffolds already on the platform without waiting on live bureau or cross-tenant governance.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants. Ingestion start remains deferred; benchmarks remain org-scoped only.

## Epic outcomes (target)

| Epic | Theme                                       | 17.0 target | Summary                                                                     |
| ---- | ------------------------------------------- | ----------- | --------------------------------------------------------------------------- |
| 1    | Reporting Center org-internal benchmarks UI | Released    | Staff UI for trailing baseline/recent outcome rates + advisory deltas       |
| 2    | Compliance Center ingestion audit UI        | Released    | Staff UI to list/status/start deferred bureau response ingestion audit runs |
| 3    | Capability matrix / governance sign-off     | Released    | Scope, checklist, matrix rows, release notes                                |

## Shipped from 16.0 (foundation — do not regress)

All v16.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — org dispute settings tolerance, bureau response ingestion audit API, and org-internal benchmarks read model. See [`version-16.0-scope.md`](version-16.0-scope.md).

## Explicit deferrals (not 17.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 18.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 18.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 18.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |

## Partial capability limits (17.0 targets)

### Reporting Center org-internal benchmarks UI (Released)

**Included:** Reporting Center panel consuming `GET /reporting/reinvestigation-outcomes/benchmarks` with baseline/recent windows, rates, and advisory deltas; optional bureau filter.

**Not included:** Cross-tenant percentile ranks; editing historical responses from the panel; exporting benchmark PII.

### Compliance Center ingestion audit UI (Released)

**Included:** Compliance Center tab for ingestion status, paginated run history, and starting a deferred scaffold run (always records `status=deferred`).

**Not included:** Live polling, webhook receivers, or auto-recording bureau mail/portal responses without staff review.

## Related documents

- [Version 17.0 completion checklist](../development/version-17.0-completion-checklist.md)
- [Release notes — v17.0.0](../release-notes/v17.0.0.md)
- [Version 16.0 scope](version-16.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
