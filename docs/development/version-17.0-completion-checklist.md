# Version 17.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 16 — Reinvestigation Operations Surfaces** and follow-on governance work.

Preceded by shipped **v16.0.0**. **Targeting v17.0.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-17.0-scope.md`](../governance/version-17.0-scope.md)

## Exit criteria for "17.0 done"

- [x] Reporting Center exposes org-internal reinvestigation outcome benchmarks
- [x] Compliance Center exposes bureau response ingestion audit runs (start stays deferred)
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v17.0.0.md` + tag `v17.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                                | Epic       | Status |
| ----- | ---------------------------------------------------- | ---------- | ------ |
| 1     | 17.0 scope + completion checklist                    | Kickoff    | ✅     |
| 2     | Reporting Center org-internal benchmarks UI          | Reporting  | ✅     |
| 3     | Compliance Center bureau response ingestion audit UI | Compliance | ✅     |
| 4     | Capability matrix 17.0 sign-off                      | Governance | ⬜     |

Slice 2 surfaces the Phase 15 benchmarks read model in Reporting Center. Slice 3 surfaces the Phase 15 ingestion audit scaffold in Compliance Center (start remains deferred — no live bureau calls). Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 17.0 (→ 18.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 18.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 18.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 18.0+   | Data governance and legal review not complete           |
