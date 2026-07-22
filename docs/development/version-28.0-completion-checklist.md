# Version 28.0 Completion Checklist

Ordered path for **Compliance Intelligence Phase 27 — Monitoring Report Parser Depth** and follow-on governance work.

Preceded by shipped **v27.0.0**. Target tag: **v28.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-28.0-scope.md`](../governance/version-28.0-scope.md)

## Exit criteria for "28.0 done"

- [x] IdentityIQ golden fixture + expected JSON regression runs in CI
- [x] Staff can parse SmartCredit monitoring / tri-merge PDFs into per-bureau tradelines
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented
- [x] `docs/release-notes/v28.0.0.md` + tag `v28.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                     | Epic           | Status |
| ----- | ----------------------------------------- | -------------- | ------ |
| 1     | 28.0 scope + completion checklist         | Kickoff        | ✅     |
| 2     | IdentityIQ golden fixture regression      | Report parsers | ✅     |
| 3     | SmartCredit monitoring / tri-merge parser | Report parsers | ✅     |
| 4     | Capability matrix 28.0 sign-off           | Governance     | ✅     |

Slice 2 hardens the shipped IdentityIQ parser with CI regression. Slice 3 adds the SmartCredit sibling layout. Live polling, automated filing, and cross-tenant benchmarks stay out of scope.

---

## Explicitly not 28.0 (→ 29.0+)

| Capability                                        | Version | Why defer                                               |
| ------------------------------------------------- | ------- | ------------------------------------------------------- |
| Live bureau response ingestion / polling          | 29.0+   | Live bureau API access + legal/compliance sign-off      |
| Automated re-dispute filing execution             | 29.0+   | Depends on deferred live submission                     |
| Unsupervised CFPB / attorney escalation           | Never   | Escalation stays an advisory, human-filed signal        |
| Automated litigation filing / e-filing            | Never   | The export is a human handoff; the platform never files |
| Cross-tenant reinvestigation-outcome benchmarks   | 29.0+   | Data governance and legal review not complete           |
| Org-specific litigation PDF letterhead            | 29.0+   | Branding / template product decision                    |
| Automatic scheduled benchmark recompute jobs      | 29.0+   | Staff on-demand read models are sufficient              |
| Response-level / PII benchmark export             | Never   | Aggregate rates only                                    |
| Automatic re-parse / re-extract on worker restart | 29.0+   | Staff enqueue remains the recovery path                 |
| New dispute scoring / LLM playbook engine         | 29.0+   | Compose existing engines first                          |
| IdentityIQ / SmartCredit live B2B pull APIs       | Never   | Not offered to CROs; client PDF import is the path      |
| MyScoreIQ / other monitoring siblings             | 29.0+   | SmartCredit first                                       |
| Mortgage Partner Edition                          | 29.0    | Edition on shared platform (no fork) — see Version 29.0 |
