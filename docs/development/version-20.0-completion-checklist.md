# Version 20.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 19 — Reinvestigation Benchmark Parity** and follow-on governance work.

Preceded by shipped **v19.0.0**. **Shipped as v20.0.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-20.0-scope.md`](../governance/version-20.0-scope.md)

## Exit criteria for "20.0 done"

- [x] Outcome benchmarks API/UI expose a per-recipient breakdown in one call
- [x] Staff can download an aggregate rates CSV (no PII) from Outcome benchmarks
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v20.0.0.md` + tag `v20.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                          | Epic       | Status |
| ----- | ---------------------------------------------- | ---------- | ------ |
| 1     | 20.0 scope + completion checklist              | Kickoff    | ✅     |
| 2     | Outcome benchmarks per-recipient breakdown     | Reporting  | ✅     |
| 3     | Org-internal benchmarks aggregate rates export | Reporting  | ✅     |
| 4     | Capability matrix 20.0 sign-off                | Governance | ✅     |

Slice 2 adds `group_by=recipient` parity with outcome analytics on the benchmarks read model. Slice 3 adds an operator-gated CSV of aggregate rates (windows + org/bureau/recipient counts/rates; no client/account IDs). Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 20.0 (→ 21.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 21.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 21.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 21.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead          | 21.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs    | 21.0+   | Staff on-demand read models are sufficient              |
| Per-recipient benchmark window defaults         | 21.0+   | Optional follow-on after recipient breakdown            |
| Response-level / PII benchmark export           | Never   | Aggregate rates only                                    |
