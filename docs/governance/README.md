# Platform Governance

This directory is the **governance hub** for the Verdin Credit Platform. It connects product direction, technical design, standards, and delivery status into one traceable system.

## Governance layers

| Layer                 | Document                                                                                                                   | Audience                    | Answers                                                    |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ---------------------------------------------------------- |
| **Product roadmap**   | [`../roadmap/README.md`](../roadmap/README.md) · [`../roadmap/v5.0-enterprise.md`](../roadmap/v5.0-enterprise.md)          | Executives, PM, engineering | Where are we going? What domains matter?                   |
| **Capability matrix** | [`capability-matrix.md`](capability-matrix.md)                                                                             | All stakeholders            | What exists today? What is production-ready?               |
| **Architecture**      | [`../architecture/README.md`](../architecture/README.md)                                                                   | Engineers, architects       | How is it built? What rules apply?                         |
| **ADRs**              | [`../adr/README.md`](../adr/README.md)                                                                                     | Engineers                   | Why was it built this way?                                 |
| **Engineering log**   | [`../engineering/changelog.md`](../engineering/changelog.md)                                                               | Engineers                   | Why did implementation choices evolve?                     |
| **Quality**           | [`../quality/README.md`](../quality/README.md)                                                                             | Engineers, QA               | How do we validate performance, security, and reliability? |
| **Release review**    | [`architecture-scorecard.md`](architecture-scorecard.md)                                                                   | Engineering leads           | Is the architecture healthy for this release?              |
| **Repository health** | [`repository-health.md`](repository-health.md)                                                                             | All stakeholders            | What is the current engineering health snapshot?           |
| **Standards**         | [`../coding-standards.md`](../coding-standards.md), [`../architecture/api-standards.md`](../architecture/api-standards.md) | Engineers                   | What conventions must we follow?                           |

## Feature lifecycle

Every feature must follow this lifecycle for consistency and traceability:

```
Roadmap alignment
       ↓
Architecture review (domain + data + API + security)
       ↓
ADR (if significant or irreversible)
       ↓
Feature branch
       ↓
Implementation (router → service → repository)
       ↓
Tests (unit + integration)
       ↓
Documentation (API reference + architecture if changed)
       ↓
Pull request
       ↓
CI/CD (pre-commit, lint, typecheck, pytest, build)
       ↓
Merge
       ↓
Release notes
       ↓
Capability matrix update   ← required before epic is "done"
```

## Release Cadence

Use a predictable release model now that the platform has a stable Operational Core:

| Channel         | Policy                                                                           |
| --------------- | -------------------------------------------------------------------------------- |
| `main`          | Always releasable. Only merge work that has passed CI and is ready to ship.      |
| `feature/*`     | Individual capabilities or tightly scoped product changes.                       |
| `sprint/*`      | Stabilization, integration, and release-hardening work.                          |
| Semantic tags   | Use annotated semantic version tags such as `v4.3.0`, `v4.3.1`, `v4.5.0`.        |
| GitHub Releases | Every tagged version gets release notes and a summary of delivered capabilities. |

Release flow:

1. Complete feature or sprint work on a branch.
2. Merge through PR after CI, review, release notes, and capability matrix updates.
3. Pull `main` locally after merge.
4. Create an annotated tag from `main`.
5. Push the tag.
6. Publish a GitHub Release from the tag with delivered capabilities, upgrade notes, and known risks.

## Release history

Current tag: **[v27.0.0](../release-notes/v27.0.0.md)**. Full milestone table: [`../roadmap/README.md`](../roadmap/README.md).

| Version     | Status   | Description                                                                            |
| ----------- | -------- | -------------------------------------------------------------------------------------- |
| v4.3.0      | Released | Initial Operational Core                                                               |
| v4.3.1      | Released | Operational Core completion (Mission Control)                                          |
| v4.5.0      | Released | Automation Platform                                                                    |
| v4.8.0      | Released | Operations (notifications, portal, LLM gates, reporting)                               |
| v5.0.0      | Released | Enterprise Edition                                                                     |
| v5.1–5.21   | Released | Production hardening through reinvestigation analytics polish                          |
| v16–v26     | Released | Reinvestigation ops → document pipeline resolution (Phases 15–25)                      |
| **v27.0.0** | Released | Dispute Playbook depth & case entity re-resolve (Phase 26)                             |
| v28.0       | Planned  | Monitoring report parser depth (IdentityIQ golden fixtures, SmartCredit) — see roadmap |

Early release notes: [`v4.3.0-ga.md`](../release-notes/v4.3.0-ga.md), [`v4.3.1.md`](../release-notes/v4.3.1.md), [`v4.5.0.md`](../release-notes/v4.5.0.md), [`v4.8.0.md`](../release-notes/v4.8.0.md), [`v5.0.0.md`](../release-notes/v5.0.0.md). Latest: [`v27.0.0.md`](../release-notes/v27.0.0.md).

## Sprint history

Sprints are engineering milestones — not semantic versions. Sprint 4.3.1 (Operational Core Stabilization) **shipped**; subsequent delivery uses versioned checklists + Cursor sprint-loop rules (`.cursor/rules/version-*-sprint-loop.mdc`).

| Sprint       | Status      | Description                                                |
| ------------ | ----------- | ---------------------------------------------------------- |
| Sprint 4.3.1 | **Shipped** | E2E gate, performance baselines, security review, coverage |

Plan (archive): [`docs/sprint-4.3.1/operational-core-stabilization.md`](../sprint-4.3.1/operational-core-stabilization.md)

### Definition of done (capability row)

A capability may be marked **✅ Production** in the [capability matrix](capability-matrix.md) only when:

- Backend module complete with RBAC and org scoping
- API documented in `docs/api/reference.md`
- `@verdin/api-client` functions implemented (not stubs)
- Frontend UI integrated (where applicable)
- Integration tests for all endpoints
- Release notes or sprint doc published
- Matrix row updated in the same PR or immediately after merge

## Recommended build order

Historical phases 1–4 (Operational Core → Automation → Intelligence → Enterprise) are **shipped**. See [`../roadmap/README.md`](../roadmap/README.md) for Versions 4.2–27.0.

### Current focus

| Priority | Capability                                        | Status     | Reference                                                                                                           |
| -------- | ------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| —        | Version 27.0 — Playbook depth & entity re-resolve | ✅ Shipped | [`version-27.0-scope.md`](version-27.0-scope.md)                                                                    |
| **Next** | Version 28.0 — Monitoring report parser depth     | Planned    | [`version-28.0-scope.md`](version-28.0-scope.md) · [checklist](../development/version-28.0-completion-checklist.md) |

Live bureau polling, automated filing, and cross-tenant benchmarks remain deferred pending legal/compliance sign-off.

### Archive — Phase 1 Operational Core (Version 4.3)

| Priority | Capability                                  | Status     |
| -------- | ------------------------------------------- | ---------- |
| —        | Platform Foundation through Mission Control | ✅ Shipped |
| —        | Sprint 4.3.1 stabilization                  | ✅ Shipped |

### Archive — Phases 2–4

- **Phase 2 — Automation (4.5):** import wizard, dispute lifecycle, workflow tasks — shipped `v4.5.0`
- **Phase 3 — Intelligence (4.8):** portal, notifications, LLM gates, reporting — shipped `v4.8.0`
- **Phase 4 — Enterprise (5.0+):** compliance, identity, production email — shipped `v5.0.0` onward

## Quick links

- [Docs hub](../README.md)
- [Architecture scorecard (release review)](architecture-scorecard.md)
- [Repository health dashboard](repository-health.md)
- [Quality hub](../quality/README.md)
- [Capability matrix (executive view)](capability-matrix.md)
- [Version 28.0 scope](version-28.0-scope.md)
- [Version 28.0 checklist](../development/version-28.0-completion-checklist.md)
- [Version 27.0 scope](version-27.0-scope.md)
- [Version 27.0 checklist](../development/version-27.0-completion-checklist.md)
- [Roadmap index](../roadmap/README.md)
- [Engineering Decision Log](../engineering/changelog.md)
- [Release notes — v27.0.0](../release-notes/v27.0.0.md)
- [Developer guide](../developer-guide.md)
- [ADR 009 — Architecture governance](../adr/009-architecture-governance.md)
