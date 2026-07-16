# Version 16.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 15 — Reinvestigation Operations & Configuration** and follow-on governance work.

Preceded by shipped **v5.21.0**. **Shipped as v16.0.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-16.0-scope.md`](../governance/version-16.0-scope.md)

## Exit criteria for "16.0 done"

- [x] Organizations can configure cross-bureau monetary tolerance (default $1.00)
- [x] Bureau response ingestion audit scaffold exposes run history (no live polling)
- [x] Org-internal reinvestigation outcome benchmarks are available as a read model
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v16.0.0.md` + tag `v16.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                           | Epic       | Status |
| ----- | ----------------------------------------------- | ---------- | ------ |
| 1     | 16.0 scope + completion checklist               | Kickoff    | ✅     |
| 2     | Org-configurable cross-bureau balance tolerance | Org Admin  | ✅     |
| 3     | Bureau response ingestion audit scaffold        | Compliance | ✅     |
| 4     | Org-internal reinvestigation outcome benchmarks | Reporting  | ✅     |
| 5     | Capability matrix 16.0 sign-off                 | Governance | ✅     |

Slice 2 moves cross-bureau monetary tolerance from a module constant to per-org dispute settings (addresses the 5.21 org-settings deferral). Slice 3 adds a compliance audit run table for planned bureau response ingestion without live API calls (addresses the long-deferred ingestion audit gap). Slice 4 adds org-scoped historical baselines on reinvestigation outcomes — advisory context only, no cross-tenant data.

---

## Explicitly not 16.0 (→ 17.0+ / 18.0+)

| Capability                                       | Version | Why defer                                               |
| ------------------------------------------------ | ------- | ------------------------------------------------------- |
| Reporting / Compliance operator UI for scaffolds | 17.0    | Surfaced in Phase 16 operations surfaces                |
| Live bureau response ingestion / polling         | 18.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution            | 18.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation          | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing           | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks  | 18.0+   | Data governance and legal review not complete           |
