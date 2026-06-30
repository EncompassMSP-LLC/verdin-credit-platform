# Architecture Decision Record 010: Platform Capability Matrix

**Status:** Accepted  
**Date:** 2026-06-28  
**Deciders:** Engineering team

## Context

With the V5.0 roadmap, architecture constitution, ADRs, and coding standards in place, stakeholders still lacked a single view answering: _What capabilities exist? Are they production-ready? What depends on what?_

Contributors needed a mandatory final step in the feature lifecycle to record delivery status.

## Decision

1. Introduce the **[Platform Capability Matrix](../governance/capability-matrix.md)** as the executive governance layer in `docs/governance/`.
2. Create **`docs/governance/README.md`** as the governance hub linking roadmap, capability matrix, architecture, ADRs, and standards.
3. Require **capability matrix updates** as the last step of the [feature lifecycle](../governance/README.md#feature-lifecycle) before an epic is considered complete.
4. Adopt the recommended **build order** with Document Intelligence Platform as the next major epic after Case Management and Credit Account Intelligence.

## Consequences

### Positive

- One-page status for executives, PM, and engineers
- Clear dependencies between capabilities (documents → OCR → AI → disputes)
- Traceability from roadmap intent to shipped reality
- Definition of done is explicit per capability row

### Negative

- Matrix must be maintained — stale rows erode trust
- Slight overhead per PR for epic-level work

## Related

- [ADR 009 — Architecture governance](009-architecture-governance.md)
- [Capability matrix](../governance/capability-matrix.md)
