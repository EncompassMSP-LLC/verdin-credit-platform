# 12 — Compliance

FCRA-aware operations, SOC2-ready controls, and edition guardrails.

## Platform anchors

- [Security architecture](../../architecture/security-architecture.md)
- Compliance Center / retention modules in `apps/api`
- Partner access audits: `partner_access_audits` (mortgage partner module)

## Non-negotiables

- No live bureau soft-pull for partners without a separate compliance program
- No unsupervised dispute filing
- No cross-tenant applicant marketplace
- Multi-tenant isolation on every query
