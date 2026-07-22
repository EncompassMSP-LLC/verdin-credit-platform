# Architecture Governance

This directory is the **technical constitution** for the Verdin Credit Platform. It defines how the system is structured today and how it evolves toward [Version 5.0 Enterprise](../roadmap/v5.0-enterprise.md).

**Capability status:** [Platform Capability Matrix](../governance/capability-matrix.md)

Every new feature, sprint, or ADR should align with these documents.

## Document index

| Document                                                | Scope                                                                        |
| ------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [v4.3.0 Architecture Snapshot](v4.3.0-snapshot.md)      | As-built Operational Core reference before Version 4.5                       |
| [System Architecture](system-architecture.md)           | High-level platform design, runtime topology, monorepo layout                |
| [Domain Model](domain-model.md)                         | Business domains, bounded contexts, entity relationships                     |
| [Data Model](data-model.md)                             | Persistence model, lifecycles, multi-tenancy rules                           |
| [API Standards](api-standards.md)                       | REST conventions, errors, versioning, pagination                             |
| [Security Architecture](security-architecture.md)       | Authentication, authorization, audit, compliance hooks                       |
| [AI Architecture](ai-architecture.md)                   | OCR, summaries, recommendations, future agent orchestration                  |
| [Overview (legacy summary)](overview.md)                | Quick-reference diagram — see system-architecture for detail                 |
| [LRP enterprise workspace](../lrp-enterprise/README.md) | Cursor docs taxonomy (00–15), app/package mapping, assets — edition not fork |

## Architecture Decision Records

Significant and irreversible decisions are recorded in [`docs/adr/`](../adr/README.md).

**Process:** Check the ADR index → copy [`template.md`](../adr/template.md) → open PR → merge when accepted.

Do not contradict an **Accepted** ADR without superseding it.

## Alignment checklist (new features)

Before merging substantial work, confirm:

- [ ] Maps to a [roadmap domain](../roadmap/v5.0-enterprise.md#core-platform-domains)
- [ ] Follows **router → service → repository** (no SQLAlchemy in routers)
- [ ] Organization-scoped with **RBAC** enforced
- [ ] Uses **UUID** keys, **UTC** timestamps, **soft delete** where applicable
- [ ] Emits **audit/timeline events** when the action is user-visible or compliance-relevant
- [ ] Documented in `docs/api/reference.md` and covered by tests
- [ ] Frontend uses `@verdin/api-client` and shared types from `@verdin/shared`

## Related documentation

- [Governance hub](../governance/README.md) — feature lifecycle
- [Capability matrix](../governance/capability-matrix.md) — production readiness
- [Product roadmap](../roadmap/README.md)
- [Engineering Decision Log](../engineering/changelog.md) — sprint-level technical rationale
- [v4.3.0 Architecture Snapshot](v4.3.0-snapshot.md) — as-built Operational Core reference
- [Developer guide](../developer-guide.md)
- [Database ERD](../database/erd.md) — diagram reference (see data-model for authoritative lifecycle detail)
- [Coding standards](../coding-standards.md)
