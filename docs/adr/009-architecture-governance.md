# Architecture Decision Record 009: Architecture governance and V5 roadmap

**Status:** Accepted  
**Date:** 2026-06-28  
**Deciders:** Engineering team

## Context

The platform has moved beyond prototype stage with production-grade modules (case management, credit account intelligence). Ad-hoc feature development risks architectural drift as the codebase grows toward enterprise capabilities.

We need a **master roadmap** and **technical constitution** so every sprint aligns with long-term platform vision.

## Decision

1. Adopt **[Version 5.0 Enterprise](../roadmap/v5.0-enterprise.md)** as the master product roadmap in `docs/roadmap/`.
2. Establish **`docs/architecture/`** as the technical constitution with indexed documents for system design, domains, API, security, AI, and data model.
3. Require new epics to map to a roadmap domain and follow architecture alignment checklist ([architecture README](README.md#alignment-checklist-new-features)).
4. Continue recording irreversible decisions as ADRs in `docs/adr/`.

## Consequences

### Positive

- Shared vocabulary for domains (Case, Account, Timeline, etc.)
- Clear version milestones (4.3 → 4.5 → 4.8 → 5.0)
- Onboarding path for engineers and AI assistants (`AGENTS.md` + architecture index)
- Sprint planning traceability

### Negative

- Documentation maintenance overhead — docs must update with significant features
- Initial time investment before coding new domains

### Neutral

- Does not change runtime code; governance is process and documentation only
- Existing ADRs 001–008 remain authoritative

## Related

- [Roadmap index](../roadmap/README.md)
- [Architecture governance README](README.md)
