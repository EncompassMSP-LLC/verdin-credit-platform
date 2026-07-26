# ADR-013: Lending Readiness Platform as an edition on the shared monorepo

**Date:** 2026-07-26  
**Authors:** Platform Engineering

## Status

Accepted

## Context

Lending Readiness Partners (LRP) needs a lender-facing product (CRM, borrower/LO portals, readiness, partner automation) while Ultimate Credit Repair LLC already operates a shared Verdin Credit Platform monorepo (`apps/api`, `apps/web`, workers, packages).

Two alternatives were considered:

1. **Fork** a separate Mortgage / LRP codebase and diverge schemas, auth, and engines.
2. **Edition** — ship LRP UX and partner RBAC on the same platform, reusing FCRA/Metro2/cross-bureau/intelligence modules and gating with org partnership flags.

A fork would duplicate compliance engines, multiply security surface, and break the claim-library / ADR-012 control plane. Product requests to “split into a separate Mortgage product” conflict with Version 29.0 scope rules.

## Decision

Deliver **Lending Readiness Platform™** as an **edition** of the Verdin Credit Platform:

| Surface                    | Location                                            |
| -------------------------- | --------------------------------------------------- |
| Partner / LO / borrower UX | `apps/lrp-web`                                      |
| CRO / staff admin          | `apps/web`                                          |
| API / RBAC / jobs          | `apps/api`, `apps/worker`                           |
| Feature gate               | `ENABLE_MORTGAGE_PARTNER` + org partnership records |

Rules:

- Prefer extending existing modules (`mortgage_partner`, `clients`, `notifications`, `documents`, `llm`, `reporting`) over new parallel engines.
- Reuse FCRA/Metro2/cross-bureau/intelligence — do not duplicate.
- No unsupervised bureau filing or live soft-pull as a V1.0 deliverable.
- LLM features call `require_llm_ready()` / ADR-012.
- Decline requests to fork the entire platform; document edition approach instead.
- Trace ops requirements → software via the [V1.0 release plan](../lrp-enterprise/15-roadmap/lending-readiness-platform-v1.0-release-plan.md).

## Consequences

### Positive

- Single compliance and security review surface
- Shared migrations, CI, and claim-library governance
- Faster delivery by wiring existing readiness/dispute foundations

### Negative

- Edition UX must stay carefully scoped so CRO and partner audiences do not leak data
- Feature flags and partner RBAC add configuration complexity

### Neutral

- Optional `apps/lender-web` only if UX must diverge further (prefer not)
- Living docs (backlog, roadmap, debt, risk) track post-V1.0 work without forking docs trees
