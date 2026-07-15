# Version 5.19 Completion Checklist

Ordered path for **Compliance Intelligence Phase 12 — Reinvestigation Analytics & Evidence Depth** and follow-on governance work.

Preceded by shipped **v5.18.0**. **Targeting v5.19.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.19-scope.md`](../governance/version-5.19-scope.md)

## Exit criteria for "5.19 done"

- [x] Reinvestigation outcome analytics support date-range + per-bureau slicing
- [x] §611 clock start / round counts split by recipient (bureau vs furnisher)
- [x] Litigation-readiness assessment folds in cross-bureau discrepancy evidence
- [x] Operator-gated litigation evidence export (text) for attorney handoff (never auto-transmits)
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v5.19.0.md` + tag `v5.19.0`

---

## Phase 1 — Recommended order

| Order | Slice                                                 | Epic       | Status |
| ----- | ----------------------------------------------------- | ---------- | ------ |
| 1     | 5.19 scope + completion checklist                     | Kickoff    | ✅     |
| 2     | Reinvestigation analytics date-range + bureau slicing | Reporting  | ✅     |
| 3     | Per-recipient reinvestigation clock splits            | Disputes   | ✅     |
| 4     | Litigation packet cross-bureau evidence               | Disputes   | ✅     |
| 5     | Operator-gated litigation evidence export             | Disputes   | ✅     |
| 6     | Capability matrix 5.19 sign-off                       | Governance | ⬜     |

Slice 2 adds optional `start`/`end`/`bureau` filters to the 5.18 outcome analytics (addresses the documented no-date-range tech debt). Slice 3 splits the clock by recipient (addresses the `dispute_round_count` recipient-agnostic tech debt). Slice 4 enriches the litigation assessment with cross-bureau discrepancy indicators. Slice 5 adds a downloadable evidence document, reusing the dispute-letter export pattern.

---

## Explicitly not 5.19 (→ 5.20+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.20+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing                     | 5.20+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 5.20+   | Data governance and legal review not complete           |
