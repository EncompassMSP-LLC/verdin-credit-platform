# Version 29.0 Scope & Deferrals

Formal scope for **Version 29.0 — Mortgage Partner Edition (foundation)**. Builds on shipped **v28.0.0** Monitoring Report Parser Depth and the existing CRO operational core (cases, parsers, FCRA/Metro2 findings, intelligence, reporting, portal).

**Kickoff date:** 2026-07-22  
**Target:** Package a **B2B lender / mortgage-partner surface on the same platform** — not a forked product — so lending partners can see pipeline readiness, bureau/FCRA issues, and milestone progress for applicants referred through CRO workflows — **without** live bureau soft-pull APIs, automated filing, or cross-tenant data sharing.

## Theme

Ultimate Credit Repair LLC remains the system of record for credit operations. Mortgage Partner Edition is a **product edition / packaging layer**: lender personas, readiness scoring, partner dashboards, and white-label branding on shared clients, cases, tradelines, and findings.

**Architecture decision (locked for 29.0):** same monorepo, same API/DB multi-tenant model, feature pack + org partnership — **do not** copy the codebase into a separate Mortgage product. A separate `apps/lender-web` is allowed only if UX divergence requires it; packages and API stay shared.

## Epic outcomes (target)

| Epic | Theme                                    | 29.0 target | Summary                                                                                |
| ---- | ---------------------------------------- | ----------- | -------------------------------------------------------------------------------------- |
| 1    | Partner org model + lender RBAC scaffold | Planned     | Org partnership (Lender ↔ CRO), lender role(s), feature flag `ENABLE_MORTGAGE_PARTNER` |
| 2    | Lender dashboard + client pipeline       | Planned     | Secure partner dashboard; pipeline stages over shared cases/clients                    |
| 3    | Mortgage readiness score + report export | Planned     | Estimator + automated readiness PDF/report from existing intelligence / findings       |
| 4    | Capability matrix / governance sign-off  | Planned     | Scope, checklist, matrix rows, release notes                                           |

## Explicitly reuse (do not rebuild)

| Existing capability             | Mortgage Partner use                         |
| ------------------------------- | -------------------------------------------- |
| Cross-bureau comparison         | Bureau comparison tools on lender case views |
| Metro2 + FCRA findings          | Compliance review + FCRA issue tracking      |
| Account / case intelligence     | Inputs to mortgage readiness estimator       |
| Reporting / packet exports      | Pattern for readiness reports                |
| Notifications / portal patterns | Lender status updates (partner channel)      |
| Tasks / playbook checklists     | Rapid rescore preparation checklist          |
| Org admin / branding config     | White-label theme hooks for lending partners |

## Explicit deferrals (not 29.0)

| Capability                                          | Deferred to | Reason                                                             |
| --------------------------------------------------- | ----------- | ------------------------------------------------------------------ |
| Full white-label multi-domain SaaS for all partners | 30.0+       | Start with theme + logo; custom domains later                      |
| Live bureau soft-pull for lenders                   | Never\*     | Same CRO constraint unless separate compliance program             |
| Automated dispute filing / bureau live APIs         | Never\*     | Unchanged platform policy                                          |
| Cross-tenant lender marketplaces                    | Never       | No sharing applicant data across unrelated lenders                 |
| LOS / Encompass / Calyx deep sync                   | 30.0+       | Partner dashboard first; LOS connectors after product-market fit   |
| Consumer-facing mortgage application portal         | 30.0+       | Lender + CRO staff surfaces first                                  |
| Separate forked Mortgage codebase                   | Never       | Edition on shared platform only                                    |
| MyScoreIQ / additional CRO parsers                  | Parallel    | Remains Version 28.0+ parser backlog; not blocked by Mortgage work |

\*Unless a future compliance-approved program explicitly revisits these gates.

## Partial capability limits (29.0 targets)

### Partner org model + lender RBAC (Shipped — staff scaffold)

**Included:** Data model for CRO↔partner org partnership; feature flag `ENABLE_MORTGAGE_PARTNER`; staff APIs for partnerships, members, referrals; partner-role permission matrix; audit of partner access.

**Not included:** Marketplace of lenders; unrestricted PII export; cross-CRO browsing; partner JWT realm (next slice).

### Lender dashboard + pipeline (Planned)

**Included:** Partner dashboard (secure, RBAC); pipeline stages (e.g. referred → in repair → mortgage-ready → in underwriting → funded/declined); loan milestone tracking on the case.

**Not included:** Full LOS replacement; automated credit decisioning that replaces lender underwriting.

### Mortgage readiness score + report (Planned)

**Included:** Deterministic readiness estimator (rules + existing scores/findings); staff/partner-triggered readiness report export; rapid rescore checklist template; AI action-plan **augmentation** only behind existing ADR-012 LLM gates.

**Not included:** Guaranteed approval predictions; unsupervised LLM without policy; Metro2 “certification” claims.

## Related documents

- [Version 29.0 completion checklist](../development/version-29.0-completion-checklist.md)
- [Version 28.0 scope](version-28.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
