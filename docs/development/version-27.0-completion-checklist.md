# Version 27.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 26 — Dispute Playbook Depth & Case Entity Re-resolve** and follow-on governance work.

Preceded by shipped **v26.0.0**. Target tag: **v27.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-27.0-scope.md`](../governance/version-27.0-scope.md)

## Exit criteria for "27.0 done"

- [x] Staff can deep-link from Dispute Playbook issues into Case Detail finding panels
- [x] Staff can enqueue case-level bulk entity re-resolve when metadata exists
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v27.0.0.md` + tag `v27.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                     | Epic       | Status |
| ----- | ----------------------------------------- | ---------- | ------ |
| 1     | 27.0 scope + completion checklist         | Kickoff    | ✅     |
| 2     | Playbook finding deep-links               | Cases      | ✅     |
| 3     | Case-level bulk entity re-resolve enqueue | Documents  | ✅     |
| 4     | Capability matrix 27.0 sign-off           | Governance | ✅     |

Slice 2 deepens the Dispute Playbook with finding-panel navigation. Slice 3 adds case-scoped bulk `document_entity_resolve` enqueue. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 27.0 (→ 28.0+)

| Capability                                        | Version | Why defer                                               |
| ------------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling          | 28.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution             | 28.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation           | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing            | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks   | 28.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead            | 28.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs      | 28.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export             | Never   | Aggregate rates only                                    |
| Automatic re-parse / re-extract on worker restart | 28.0+   | Staff enqueue remains the recovery path                 |
| New dispute scoring / LLM playbook engine         | 28.0+   | Compose existing engines first                          |
