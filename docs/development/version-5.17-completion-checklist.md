# Version 5.17 Completion Checklist

Ordered path for **Compliance Intelligence Phase 10 — Dispute Response Intake & Reinvestigation Tracking** and follow-on governance work.

Preceded by shipped **v5.16.0**. **Targeting v5.17.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.17-scope.md`](../governance/version-5.17-scope.md)

## Exit criteria for "5.17 done"

- [ ] Bureau/furnisher dispute responses persist as auditable per-letter records (staff-entered; no live polling)
- [ ] FCRA §611 reinvestigation clock computes deadlines and surfaces no-response / overdue states
- [ ] Reinvestigation outcomes classify and drive advisory re-dispute / escalation readiness (never auto-files)
- [ ] Per-case reinvestigation summary read model + Case Center surface
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v5.17.0.md` + tag `v5.17.0`

---

## Phase 1 — Recommended order

| Order | Slice                                          | Epic                    | Status |
| ----- | ---------------------------------------------- | ----------------------- | ------ |
| 1     | 5.17 scope + completion checklist              | Kickoff                 | ✅     |
| 2     | Dispute response intake + persistence          | Disputes                | ✅     |
| 3     | §611 reinvestigation clock & no-response       | Compliance Intelligence | ✅     |
| 4     | Reinvestigation outcome & re-dispute readiness | Disputes                | ⬜     |
| 5     | Case reinvestigation summary read model + UI   | Compliance Intelligence | ⬜     |
| 6     | Capability matrix 5.17 sign-off                | Governance              | ⬜     |

Slice 2 persists responses against sent dispute letters. Slice 3 reuses each letter's `sent_at`. Slice 4 reuses litigation-strength / dispute-strategy signals and respects 5.16 identity-theft locks. Slice 5 aggregates slices 2–4 into a per-case read model.

---

## Explicitly not 5.17 (→ 5.18+)

| Capability                                      | Version | Why defer                                          |
| ----------------------------------------------- | ------- | -------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.18+   | Live bureau API access + legal/compliance sign-off |
| Automated re-dispute filing                     | 5.18+   | Depends on deferred live submission                |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal   |
| Cross-tenant reinvestigation-outcome benchmarks | 5.18+   | Data governance and legal review not complete      |
