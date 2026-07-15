# Version 5.18 Completion Checklist

Ordered path for **Compliance Intelligence Phase 11 — Reinvestigation Depth & Litigation Readiness** and follow-on governance work.

Preceded by shipped **v5.17.0**. **Targeting v5.18.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.18-scope.md`](../governance/version-5.18-scope.md)

## Exit criteria for "5.18 done"

- [x] Each sent dispute round carries its own `sent_at`-keyed §611 reinvestigation clock
- [x] Extended 45-day reinvestigation window modeled when documents are added mid-window
- [x] Per-org reinvestigation outcome analytics read model + staff surface
- [x] Operator-gated litigation-readiness evidence packet for attorney handoff (never auto-files)
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v5.18.0.md` + tag `v5.18.0`

---

## Phase 1 — Recommended order

| Order | Slice                                        | Epic                    | Status |
| ----- | -------------------------------------------- | ----------------------- | ------ |
| 1     | 5.18 scope + completion checklist            | Kickoff                 | ✅     |
| 2     | Per-letter multi-round reinvestigation clock | Compliance Intelligence | ✅     |
| 3     | Extended 45-day reinvestigation window       | Compliance Intelligence | ✅     |
| 4     | Reinvestigation outcome analytics read model | Reporting               | ✅     |
| 5     | Litigation-readiness evidence packet         | Disputes                | ✅     |
| 6     | Capability matrix 5.18 sign-off              | Governance              | ✅     |

Slice 2 keys the clock off each `dispute_letters.sent_at` (addresses the 5.17 slice-3 single-round limitation). Slice 3 models the §611 45-day extension on top. Slice 4 aggregates recorded outcomes into per-org trends. Slice 5 bundles the evidence trail for attorney handoff, building on the 5.17 `escalate_attorney` readiness signal.

---

## Explicitly not 5.18 (→ 5.19+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.19+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing                     | 5.19+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The packet is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 5.19+   | Data governance and legal review not complete           |
