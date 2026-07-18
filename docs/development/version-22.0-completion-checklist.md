# Version 22.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 21 — Document Pipeline Hardening** and follow-on governance work.

Preceded by shipped **v21.0.0**. Target tag: **v22.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-22.0-scope.md`](../governance/version-22.0-scope.md)

## Exit criteria for "22.0 done"

- [ ] `document_metadata.payment_status` accepts bureau status narratives (varchar 255)
- [ ] Staff can re-enqueue credit report parse for eligible documents
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v22.0.0.md` + tag `v22.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                             | Epic       | Status |
| ----- | --------------------------------- | ---------- | ------ |
| 1     | 22.0 scope + completion checklist | Kickoff    | ✅     |
| 2     | Widen metadata payment_status     | Documents  | ☐      |
| 3     | Operator re-parse credit report   | Documents  | ☐      |
| 4     | Capability matrix 22.0 sign-off   | Governance | ☐      |

Slice 2 widens `payment_status` so metadata extract no longer fails on long bureau text. Slice 3 adds an operator-gated re-parse enqueue for classified credit reports with OCR. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 22.0 (→ 23.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 23.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 23.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 23.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead          | 23.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs    | 23.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export           | Never   | Aggregate rates only                                    |
