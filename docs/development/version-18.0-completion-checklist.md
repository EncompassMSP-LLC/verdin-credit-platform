# Version 18.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 17 — Reinvestigation Operations Polish** and follow-on governance work.

Preceded by shipped **v17.0.0**. **Shipped as v18.0.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-18.0-scope.md`](../governance/version-18.0-scope.md)

## Exit criteria for "18.0 done"

- [x] Organizations can configure default reinvestigation benchmark windows
- [x] Compliance Center ingestion audit supports case/account scope in UI
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v18.0.0.md` + tag `v18.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                      | Epic       | Status |
| ----- | ------------------------------------------ | ---------- | ------ |
| 1     | 18.0 scope + completion checklist          | Kickoff    | ✅     |
| 2     | Org-configurable benchmark window defaults | Org Admin  | ✅     |
| 3     | Ingestion audit case/account scope UI      | Compliance | ✅     |
| 4     | Capability matrix 18.0 sign-off            | Governance | ✅     |

Slice 2 stores org default baseline/recent window days and wires Reporting Center to them. Slice 3 exposes existing API case/account fields in the Compliance Center ingestion audit UI. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 18.0 (→ 19.0 / 20.0+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Per-bureau benchmark windows / benchmarks depth | 19.0    | Surfaced in Phase 18 benchmark depth                    |
| Live bureau response ingestion / polling        | 20.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution           | 20.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 20.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead          | 20.0+   | Branding / template product decision                    |
