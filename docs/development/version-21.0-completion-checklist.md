# Version 21.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 20 — Reinvestigation Operations Filters** and follow-on governance work.

Preceded by shipped **v20.0.0**. Target tag: **v21.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-21.0-scope.md`](../governance/version-21.0-scope.md)

## Exit criteria for "21.0 done"

- [ ] Organizations can configure optional per-recipient benchmark window overrides
- [ ] Compliance Center ingestion run list filters by bureau target and status
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v21.0.0.md` + tag `v21.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                      | Epic       | Status |
| ----- | ------------------------------------------ | ---------- | ------ |
| 1     | 21.0 scope + completion checklist          | Kickoff    | ✅     |
| 2     | Per-recipient benchmark window defaults    | Org Admin  | ☐      |
| 3     | Ingestion audit bureau/status list filters | Compliance | ☐      |
| 4     | Capability matrix 21.0 sign-off            | Governance | ☐      |

Slice 2 adds optional credit_bureau / furnisher window overrides on dispute settings (falls back to org-wide 90/30). Slice 3 adds `bureau_target` + `status` filters on the ingestion audit run list. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 21.0 (→ 22.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 22.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 22.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 22.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead          | 22.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs    | 22.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export           | Never   | Aggregate rates only                                    |
