# Version 5.21 Completion Checklist

Ordered path for **Compliance Intelligence Phase 14 — Reinvestigation Analytics & Evidence Polish** and follow-on governance work.

Preceded by shipped **v5.20.0**. **Shipped as v5.21.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.21-scope.md`](../governance/version-5.21-scope.md)

## Exit criteria for "5.21 done"

- [x] Reinvestigation outcome analytics support a single-call per-recipient breakdown
- [x] Cross-bureau discrepancy detection compares high_balance and credit_limit
- [x] Operator-gated litigation evidence PDF uses a structured multi-section layout
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v5.21.0.md` + tag `v5.21.0`

---

## Phase 1 — Recommended order

| Order | Slice                                               | Epic       | Status |
| ----- | --------------------------------------------------- | ---------- | ------ |
| 1     | 5.21 scope + completion checklist                   | Kickoff    | ✅     |
| 2     | Per-recipient reinvestigation analytics breakdown   | Reporting  | ✅     |
| 3     | Cross-bureau high_balance + credit_limit comparison | Disputes   | ✅     |
| 4     | Structured PDF litigation evidence export layout    | Disputes   | ✅     |
| 5     | Capability matrix 5.21 sign-off                     | Governance | ✅     |

Slice 2 adds `group_by=recipient` so operators compare bureau vs furnisher outcomes in one response (addresses the 5.20 bureau-only `group_by` tech debt). Slice 3 compares `high_balance` and `credit_limit` across sibling bureaus with the existing $1.00 tolerance (addresses unused monetary fields). Slice 4 upgrades the litigation PDF from wrapped text to a structured multi-section layout (addresses the simple-canvas tech debt).

---

## Explicitly not 5.21 (→ 16.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.22+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing                     | 5.22+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 5.22+   | Data governance and legal review not complete           |
| Org-configurable cross-bureau balance tolerance | 16.0+   | Needs org-settings product decision                     |
