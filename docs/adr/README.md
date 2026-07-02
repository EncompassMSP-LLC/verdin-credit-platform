# Architecture Decision Records (ADR)

This directory documents significant architectural and technical decisions for the Verdin Credit Platform. ADRs provide context for future contributors and prevent the same debates from recurring.

## When to write an ADR

Create an ADR when a decision:

- Affects multiple applications, packages, or teams
- Is difficult or expensive to reverse
- Introduces a new pattern, tool, or integration
- Has trade-offs that should be recorded explicitly

Skip ADRs for routine bug fixes, single-file refactors, or decisions that are obvious from existing conventions.

## Process

1. **Check the index** below for an existing ADR on the topic.
2. **Copy** [`template.md`](template.md) to the next numbered file (e.g. `009-my-decision.md`).
3. **Fill in** Status, Context, Decision, and Consequences.
4. **Open a PR** targeting `develop`. Architectural ADRs require review from at least two team members (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md)).
5. **Merge** once accepted. Update the ADR index in this README.
6. **Update** the [capability matrix](../governance/capability-matrix.md) when the decision ships a new or changed capability.

## Status values

| Status     | Meaning                              |
| ---------- | ------------------------------------ |
| Proposed   | Under discussion; not yet adopted    |
| Accepted   | Active decision for the codebase     |
| Deprecated | Superseded or no longer recommended  |
| Superseded | Replaced by a newer ADR (link to it) |

## File naming

```
NNN-short-title.md
```

- `NNN` — three-digit sequence (`005`, `006`, …)
- `short-title` — lowercase, hyphen-separated topic

One decision per file. Do not append new decisions to existing ADR files.

## ADR index

| ADR                                   | Title                                  | Status   |
| ------------------------------------- | -------------------------------------- | -------- |
| [001](001-monorepo.md)                | Monorepo with pnpm and Turborepo       | Accepted |
| [002](001-monorepo.md)                | Layered backend architecture           | Accepted |
| [003](001-monorepo.md)                | UUID primary keys                      | Accepted |
| [004](001-monorepo.md)                | JWT with refresh tokens                | Accepted |
| [005](005-domain-modules.md)          | Domain-driven API modules              | Accepted |
| [006](006-api-versioning.md)          | URL-based API versioning               | Accepted |
| [007](007-quality-gates.md)           | Quality gates (pre-commit and CI)      | Accepted |
| [008](008-background-jobs.md)         | Redis-backed background jobs           | Accepted |
| [009](009-architecture-governance.md) | Architecture governance and V5 roadmap | Accepted |
| [010](010-capability-matrix.md)       | Platform capability matrix             | Accepted |
| [011](011-job-orchestrator.md)        | Unified job orchestration package      | Accepted |
| [012](012-llm-provider-policy.md)     | LLM provider policy and feature gates  | Accepted |

> **Note:** ADRs 001–004 were recorded in a single legacy file before the formal template was introduced. New ADRs from 005 onward follow [`template.md`](template.md).

## Related documentation

- [`docs/governance/capability-matrix.md`](../governance/capability-matrix.md) — platform capability status
- [`docs/governance/README.md`](../governance/README.md) — feature lifecycle
- [`docs/roadmap/v5.0-enterprise.md`](../roadmap/v5.0-enterprise.md) — master product roadmap
- [`docs/architecture/overview.md`](../architecture/overview.md) — system overview
- [`docs/developer-guide.md`](../developer-guide.md) — day-to-day development
- [`AGENTS.md`](../../AGENTS.md) — AI-assisted development rules
