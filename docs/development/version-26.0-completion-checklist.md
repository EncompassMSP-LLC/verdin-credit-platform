# Version 26.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 25 — Document Pipeline Resolution & Operator Surfaces** and follow-on governance work.

Preceded by shipped **v25.0.0**. Target tag: **v26.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-26.0-scope.md`](../governance/version-26.0-scope.md)

## Exit criteria for "26.0 done"

- [ ] Staff can run case bulk recovery actions without a classified credit report present
- [ ] Staff can enqueue async entity re-resolve when metadata exists
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v26.0.0.md` + tag `v26.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                    | Epic       | Status |
| ----- | ---------------------------------------- | ---------- | ------ |
| 1     | 26.0 scope + completion checklist        | Kickoff    | ✅     |
| 2     | Case Documents recovery panel            | Documents  | ☐      |
| 3     | Operator async entity re-resolve enqueue | Documents  | ☐      |
| 4     | Capability matrix 26.0 sign-off          | Governance | ☐      |

Slice 2 ungates existing bulk recovery APIs on Case Detail when any case documents exist. Slice 3 adds an operator-gated async entity re-resolve enqueue for documents with metadata. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 26.0 (→ 27.0+)

| Capability                                        | Version | Why defer                                               |
| ------------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling          | 27.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution             | 27.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation           | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing            | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks   | 27.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead            | 27.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs      | 27.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export             | Never   | Aggregate rates only                                    |
| Automatic re-parse / re-extract on worker restart | 27.0+   | Staff enqueue remains the recovery path                 |
| Case-level bulk entity re-resolve                 | 27.0+   | Single-document async re-resolve ships first            |
