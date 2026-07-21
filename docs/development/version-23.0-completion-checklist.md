# Version 23.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 22 — Document Pipeline Recovery Depth** and follow-on governance work.

Preceded by shipped **v22.0.0**. Target tag: **v23.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-23.0-scope.md`](../governance/version-23.0-scope.md)

## Exit criteria for "23.0 done"

- [x] Staff can enqueue async metadata re-extract for OCR'd documents
- [x] Staff can bulk re-parse eligible credit reports on a case
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v23.0.0.md` + tag `v23.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                  | Epic       | Status |
| ----- | -------------------------------------- | ---------- | ------ |
| 1     | 23.0 scope + completion checklist      | Kickoff    | ✅     |
| 2     | Operator async metadata re-extract     | Documents  | ✅     |
| 3     | Case-level bulk credit-report re-parse | Documents  | ✅     |
| 4     | Capability matrix 23.0 sign-off        | Governance | ☐      |

Slice 2 adds an operator-gated async metadata extract enqueue (parity with single-document re-parse). Slice 3 adds case-scoped bulk re-parse for eligible credit reports. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 23.0 (→ 24.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 24.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 24.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 24.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead          | 24.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs    | 24.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export           | Never   | Aggregate rates only                                    |
| Automatic re-parse on worker restart            | 24.0+   | Staff enqueue remains the recovery path                 |
