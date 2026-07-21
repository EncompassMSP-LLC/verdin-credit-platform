# Version 24.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 23 — Document Pipeline Recovery Parity** and follow-on governance work.

Preceded by shipped **v23.0.0**. Target tag: **v24.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-24.0-scope.md`](../governance/version-24.0-scope.md)

## Exit criteria for "24.0 done"

- [x] Staff can bulk re-extract metadata for OCR'd documents on a case
- [ ] Staff can re-enqueue document classification when OCR exists
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v24.0.0.md` + tag `v24.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                 | Epic       | Status |
| ----- | ------------------------------------- | ---------- | ------ |
| 1     | 24.0 scope + completion checklist     | Kickoff    | ✅     |
| 2     | Case-level bulk metadata re-extract   | Documents  | ✅     |
| 3     | Operator re-classify document enqueue | Documents  | ☐      |
| 4     | Capability matrix 24.0 sign-off       | Governance | ☐      |

Slice 2 adds case-scoped bulk metadata re-extract (parity with bulk credit-report re-parse). Slice 3 adds an operator-gated re-classify enqueue for OCR'd documents. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 24.0 (→ 25.0+)

| Capability                                        | Version | Why defer                                               |
| ------------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling          | 25.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution             | 25.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation           | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing            | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks   | 25.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead            | 25.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs      | 25.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export             | Never   | Aggregate rates only                                    |
| Automatic re-parse / re-extract on worker restart | 25.0+   | Staff enqueue remains the recovery path                 |
