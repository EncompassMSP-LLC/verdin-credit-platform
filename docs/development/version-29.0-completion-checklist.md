# Version 29.0 Completion Checklist

Ordered path for **Mortgage Partner Edition (foundation)** and follow-on governance work.

Preceded by shipped **v28.0.0**. Target tag: **v29.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-29.0-scope.md`](../governance/version-29.0-scope.md)

## Exit criteria for "29.0 done"

- [ ] Lender/partner org model + RBAC + `ENABLE_MORTGAGE_PARTNER` gate
- [ ] Lender dashboard with client pipeline + loan milestones (shared case data)
- [ ] Mortgage readiness estimator + exportable readiness report
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented (no fork; no live bureau; no cross-tenant marketplace)
- [ ] `docs/release-notes/v29.0.0.md` + tag `v29.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                              | Epic         | Status |
| ----- | -------------------------------------------------- | ------------ | ------ |
| 1     | 29.0 scope + completion checklist                  | Kickoff      | ✅     |
| 2     | Partner org model + lender RBAC + feature flag     | Platform     | ☐      |
| 3     | Lender dashboard + pipeline + loan milestones      | Partner UI   | ☐      |
| 4     | Mortgage readiness score + readiness report export | Intelligence | ☐      |
| 5     | Capability matrix 29.0 sign-off                    | Governance   | ☐      |

Architecture rule: **edition on the shared platform** — same monorepo/API. Do not clone the product. Optional `apps/lender-web` only if UX divergence requires it.

---

## Explicitly not 29.0 (→ 30.0+ / never)

| Capability                                     | Version | Why defer                           |
| ---------------------------------------------- | ------- | ----------------------------------- |
| Custom partner domains / full white-label SaaS | 30.0+   | Theme + logo first                  |
| LOS deep sync (Encompass, etc.)                | 30.0+   | Prove partner dashboard value first |
| Consumer mortgage application portal           | 30.0+   | Lender/CRO surfaces first           |
| Live bureau soft-pull for lenders              | Never\* | Compliance gate unchanged           |
| Automated filing / unsupervised loops          | Never\* | Platform policy unchanged           |
| Cross-tenant lender marketplace                | Never   | Applicant data isolation            |
| Forked separate Mortgage codebase              | Never   | Maintenance and compliance cost     |

\*Unless a future compliance-approved program revisits these gates.
