# Version 21.0 Scope & Deferrals

Formal scope for **Version 21.0 — Reinvestigation Operations Filters (Compliance Intelligence Phase 20)**. Builds on shipped **v20.0.0** Reinvestigation Benchmark Parity (Phase 19).

**Kickoff date:** 2026-07-17  
**Target:** Close remaining non-blocked configuration and audit-filter gaps — optional per-recipient (credit bureau vs furnisher) benchmark window defaults on dispute settings, and Compliance Center ingestion audit list filters for `bureau_target` and `status` — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

20.0 added benchmarks `group_by=recipient` and aggregate CSV export, but Reporting still uses org/bureau window resolution when comparing CRA vs furnisher clocks, and Compliance Center ingestion run lists cannot filter by the bureau target or run status already stored on each audit row. Phase 20 is non-blocked polish over configuration and audit surfaces the platform already owns.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                      | 21.0 target | Summary                                                                                        |
| ---- | ------------------------------------------ | ----------- | ---------------------------------------------------------------------------------------------- |
| 1    | Per-recipient benchmark window defaults    | Released    | Optional credit_bureau / furnisher window overrides on dispute settings; fall back to org pair |
| 2    | Ingestion audit bureau/status list filters | Released    | Optional `bureau_target` + `status` on Compliance Center ingestion run list                    |
| 3    | Capability matrix / governance sign-off    | Planned     | Scope, checklist, matrix rows, release notes                                                   |

## Shipped from 20.0 (foundation — do not regress)

All v20.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — benchmarks `group_by=recipient`, aggregate rates CSV export, and prior bureau window / reporting surfaces. See [`version-20.0-scope.md`](version-20.0-scope.md).

## Explicit deferrals (not 21.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 22.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 22.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 22.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead          | 22.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs    | 22.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export           | Never       | Aggregate rates only; no client/account IDs in export          |

## Partial capability limits (21.0 targets)

### Per-recipient benchmark window defaults (Released)

**Included:** Optional per-recipient `baseline_days` / `recent_days` overrides (`credit_bureau` / `furnisher`) on organization dispute settings; resolve when Reporting requests `group_by=recipient` or filters by recipient context; Org Admin UI to edit overrides; fall back to org-wide pair then platform defaults (90/30).

**Not included:** Per-bureau×recipient matrix; automatic scheduled recompute jobs; cross-tenant baselines.

### Ingestion audit bureau/status list filters (Released)

**Included:** Optional `bureau_target` and `status` query params on the bureau response ingestion run list API; Compliance Center list filter controls; no change to start-from-deferred behavior.

**Not included:** Live polling; webhooks; auto-recording responses; changing deferred start semantics.

## Related documents

- [Version 21.0 completion checklist](../development/version-21.0-completion-checklist.md)
- [Version 20.0 scope](version-20.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
