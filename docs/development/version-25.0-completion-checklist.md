# Version 25.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 24 — Document Pipeline Recovery Bulk Closeout** and follow-on governance work.

Preceded by shipped **v24.0.0**. Target tag: **v25.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-25.0-scope.md`](../governance/version-25.0-scope.md)

## Exit criteria for "25.0 done"

- [x] Staff can bulk re-classify OCR'd documents on a case
- [x] Staff can bulk retry OCR for failed eligible documents on a case
- [x] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v25.0.0.md` + tag `v25.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                   | Epic       | Status |
| ----- | --------------------------------------- | ---------- | ------ |
| 1     | 25.0 scope + completion checklist       | Kickoff    | ✅     |
| 2     | Case-level bulk re-classify enqueue     | Documents  | ✅     |
| 3     | Case-level bulk OCR retry (failed docs) | Documents  | ✅     |
| 4     | Capability matrix 25.0 sign-off         | Governance | ☐      |

Slice 2 adds case-scoped bulk re-classify (parity with single-document re-classify and other case bulk recovery actions). Slice 3 adds case-scoped bulk OCR retry for failed eligible documents. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 25.0 (→ 26.0+)

| Capability                                        | Version | Why defer                                               |
| ------------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling          | 26.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution             | 26.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation           | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing            | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks   | 26.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead            | 26.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs      | 26.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export             | Never   | Aggregate rates only                                    |
| Automatic re-parse / re-extract on worker restart | 26.0+   | Staff enqueue remains the recovery path                 |
