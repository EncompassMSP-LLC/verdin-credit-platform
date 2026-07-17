# Version 20.0 Scope & Deferrals

Formal scope for **Version 20.0 — Reinvestigation Benchmark Parity (Compliance Intelligence Phase 19)**. Builds on shipped **v19.0.0** Reinvestigation Benchmark Depth (Phase 18).

**Kickoff date:** 2026-07-17  
**Target:** Close parity gaps on org-internal outcome benchmarks — single-call `group_by=recipient` on the benchmarks read model (matching outcome analytics), and an operator-gated aggregate rates CSV export with **no PII** — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

19.0 added per-bureau window defaults and benchmarks `group_by=bureau`, but comparing CRA vs furnisher benchmark rates still requires multiple round-trips (or a switch to outcome analytics), and staff cannot download the aggregate rates table for handoff. Phase 19 is non-blocked parity over analytics and export surfaces the platform already owns.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                          | 20.0 target | Summary                                                                                |
| ---- | ---------------------------------------------- | ----------- | -------------------------------------------------------------------------------------- |
| 1    | Outcome benchmarks per-recipient breakdown     | Released    | `group_by=recipient` on benchmarks API + Reporting Center Bureau/Recipient control     |
| 2    | Org-internal benchmarks aggregate rates export | Planned     | Operator-gated CSV of windows + org/bureau/recipient rates (counts/rates only; no PII) |
| 3    | Capability matrix / governance sign-off        | Planned     | Scope, checklist, matrix rows, release notes                                           |

## Shipped from 19.0 (foundation — do not regress)

All v19.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — per-bureau window defaults, Outcome benchmarks `group_by=bureau`, and prior dispute-settings / ingestion surfaces. See [`version-19.0-scope.md`](version-19.0-scope.md).

## Explicit deferrals (not 20.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 21.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 21.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 21.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead          | 21.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs    | 21.0+       | Staff on-demand read models are sufficient                     |
| Per-recipient benchmark window defaults         | 21.0+       | Optional follow-on after recipient breakdown ships             |
| Response-level / PII benchmark export           | Never       | Aggregate rates only; no client/account IDs in export          |

## Partial capability limits (20.0 targets)

### Outcome benchmarks per-recipient breakdown (Released)

**Included:** Optional `group_by=recipient` on `GET /reporting/reinvestigation-outcomes/benchmarks` returning per-recipient baseline/recent analytics and advisory rate deltas (credit_bureau / furnisher / unknown); Reporting Center Bureau/Recipient breakdown control mirroring outcome analytics.

**Not included:** Cross-tenant percentile ranks; editing historical responses from the panel; exporting benchmark PII.

### Org-internal benchmarks aggregate rates export (Planned)

**Included:** Operator-gated download (CSV) of org aggregate + optional `by_bureau` / `by_recipient` rates and window metadata from the Outcome benchmarks surface; counts and rates only.

**Not included:** Response-level rows; client/account identifiers; cross-tenant exports; automatic email delivery.

## Related documents

- [Version 20.0 completion checklist](../development/version-20.0-completion-checklist.md)
- [Version 19.0 scope](version-19.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
