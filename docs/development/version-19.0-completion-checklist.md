# Version 19.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 18 — Reinvestigation Benchmark Depth** and follow-on governance work.

Preceded by shipped **v18.0.0**. **Shipped as v19.0.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-19.0-scope.md`](../governance/version-19.0-scope.md)

## Exit criteria for "19.0 done"

- [x] Organizations can configure optional per-bureau benchmark window overrides
- [x] Outcome benchmarks API/UI expose a per-bureau breakdown in one call
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v19.0.0.md` + tag `v19.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                   | Epic       | Status |
| ----- | --------------------------------------- | ---------- | ------ |
| 1     | 19.0 scope + completion checklist       | Kickoff    | ✅     |
| 2     | Per-bureau benchmark window defaults    | Org Admin  | ✅     |
| 3     | Outcome benchmarks per-bureau breakdown | Reporting  | ✅     |
| 4     | Capability matrix 19.0 sign-off         | Governance | ✅     |

Slice 2 adds optional Equifax/Experian/TransUnion window overrides on dispute settings (falls back to org-wide 90/30). Slice 3 adds `group_by=bureau` parity with outcome analytics on the benchmarks read model. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 19.0 (→ 20.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 20.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 20.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 20.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead          | 20.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs    | 20.0+   | Staff on-demand read models are sufficient              |
