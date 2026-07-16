# Version 16.0 Scope & Deferrals

Formal scope for **Version 16.0 — Reinvestigation Operations & Configuration (Compliance Intelligence Phase 15)**. Builds on shipped **v5.21.0** Reinvestigation Analytics & Evidence Polish (Phase 14).

**Kickoff date:** 2026-07-16  
**Target:** Close the configuration and operations gaps deferred from 5.21 — org-configurable cross-bureau monetary tolerance, a bureau response ingestion audit scaffold, and org-internal reinvestigation outcome benchmarks — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

5.21 polished analytics and evidence exports but left reinvestigation operations configuration hard-coded: cross-bureau comparison uses a module-level $1.00 tolerance, bureau responses are staff-entered only with no ingestion audit trail, and outcome analytics lack org-internal benchmark baselines. Phase 15 adds compliance-gated configuration and audit scaffolds over data and workflows the platform already owns.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants. Ingestion and benchmark scaffolds record intent and readiness — they do not execute deferred live integrations.

## Epic outcomes (target)

| Epic | Theme                                           | 16.0 target | Summary                                                                               |
| ---- | ----------------------------------------------- | ----------- | ------------------------------------------------------------------------------------- |
| 1    | Org-configurable cross-bureau balance tolerance | Planned     | Per-org monetary tolerance for cross-bureau discrepancy detection (default $1.00)     |
| 2    | Bureau response ingestion audit scaffold        | Planned     | Compliance audit run table + list/status API for planned ingestion (no live polling)  |
| 3    | Org-internal reinvestigation benchmark scaffold | Planned     | Org-scoped historical baseline read model on outcome analytics (no cross-tenant data) |
| 4    | Capability matrix / governance sign-off         | Planned     | Scope, checklist, matrix rows, release notes                                          |

## Shipped from 5.21 (foundation — do not regress)

All v5.21.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — per-recipient analytics breakdown, cross-bureau high_balance/credit_limit comparison, and structured PDF litigation export. See [`version-5.21-scope.md`](version-5.21-scope.md).

## Explicit deferrals (not 16.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 17.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 17.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 17.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |

## Partial capability limits (16.0 targets)

### Org-configurable cross-bureau balance tolerance (Planned)

**Included:** Per-organization `cross_bureau_balance_tolerance` (Decimal, default $1.00) stored in org dispute settings; read/write via org-admin API; wired into litigation-packet cross-bureau evidence using the org value when present.

**Not included:** Per-tradeline tolerance; tolerance for non-monetary fields; live bureau comparison beyond stored data.

### Bureau response ingestion audit scaffold (Planned)

**Included:** `bureau_response_ingestion_runs` audit table + list/get endpoints under compliance; records operator-initiated or scheduled **scaffold** runs with status, case/account scope, and deferral reason — no external bureau API calls.

**Not included:** Live polling, webhook receivers, or auto-recording bureau mail/portal responses without staff review.

### Org-internal reinvestigation benchmark scaffold (Planned)

**Included:** `GET /reporting/reinvestigation-outcomes/benchmarks` returning org-scoped historical baselines (e.g. trailing 90-day verified/deleted rates) computed from the org's own stored responses — advisory comparison context for operators.

**Not included:** Cross-tenant percentile ranks; publishing benchmarks outside the org; any PII export.

## Related documents

- [Version 16.0 completion checklist](../development/version-16.0-completion-checklist.md)
- [Version 5.21 scope](version-5.21-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
