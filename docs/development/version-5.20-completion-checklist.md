# Version 5.20 Completion Checklist

Ordered path for **Compliance Intelligence Phase 13 — Reinvestigation Analytics & Evidence Refinement** and follow-on governance work.

Preceded by shipped **v5.19.0**. **Targeting v5.20.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.20-scope.md`](../governance/version-5.20-scope.md)

## Exit criteria for "5.20 done"

- [x] Reinvestigation outcome analytics support a single-call per-bureau breakdown
- [x] §611(a)(1)(B) extended-window flag computed per recipient sub-clock
- [x] Operator-gated litigation evidence export supports a PDF format
- [ ] Cross-bureau discrepancy detection gains a balance tolerance band + extra fields
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v5.20.0.md` + tag `v5.20.0`

---

## Phase 1 — Recommended order

| Order | Slice                                            | Epic       | Status |
| ----- | ------------------------------------------------ | ---------- | ------ |
| 1     | 5.20 scope + completion checklist                | Kickoff    | ✅     |
| 2     | Per-bureau reinvestigation analytics breakdown   | Reporting  | ✅     |
| 3     | Per-recipient extended-window accuracy           | Disputes   | ✅     |
| 4     | PDF litigation evidence export                   | Disputes   | ✅     |
| 5     | Cross-bureau discrepancy tolerance + field depth | Disputes   | ⬜     |
| 6     | Capability matrix 5.20 sign-off                  | Governance | ⬜     |

Slice 2 adds an optional `group_by=bureau` breakdown so operators compare all bureaus in one response (addresses the 5.19 no-single-call-breakdown tech debt). Slice 3 computes the §611 45-day flag per recipient sub-clock (addresses the tradeline-level `extended` tech debt). Slice 4 adds a `pdf` format to the litigation evidence export, reusing the reportlab pipeline (addresses the text-only tech debt). Slice 5 gives cross-bureau detection a balance tolerance band and additional compared fields (addresses the any-difference balance-conflict tech debt).

---

## Explicitly not 5.20 (→ 5.21+)

| Capability                                      | Version | Why defer                                               |
| ----------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.21+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing                     | 5.21+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation         | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing          | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks | 5.21+   | Data governance and legal review not complete           |
