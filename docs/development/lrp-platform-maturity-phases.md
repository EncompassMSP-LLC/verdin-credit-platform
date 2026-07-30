# LRP Platform Maturity Phases

Shared monorepo edition (not a fork). Maps product maturity to the release train.

| Field        | Value                                                                         |
| ------------ | ----------------------------------------------------------------------------- |
| Last updated | 2026-07-30                                                                    |
| Master epic  | [#419](https://github.com/EncompassMSP-LLC/verdin-credit-platform/issues/419) |
| Current      | Phase 4 Growth — executing **V1.2**                                           |

## Phase overview

| Phase | Theme                | Status             | Notes                                                                                        |
| ----- | -------------------- | ------------------ | -------------------------------------------------------------------------------------------- |
| 1     | Foundation           | ✅ Complete        | Multi-tenant, CRM, cases, CRO, security, observability, release process                      |
| 2     | Core product         | ✅ Complete        | Ingestion, explainability, vault, letters, mortgage partner, timelines, unwanted-call, audit |
| 3     | Production hardening | ✅ Mostly complete | CI/CD, perf budgets, smoke E2E, docs; ops signature + DR drill still open                    |
| 4     | Growth               | 🔄 In progress     | Customer experience → automation → analytics → enterprise                                    |

## Release train (Phase 4)

```text
V1.2 — Customer Experience
V1.3 — Automation & Integrations
V1.4 — Analytics & Intelligence
V2.0 — Enterprise Platform
```

Checklists:

- [V1.2](lrp-platform-v1.2-completion-checklist.md) ← **active**
- V1.3 / V1.4 / V2.0 — open when prior train closes

## Explicit non-goals (all phases)

- Unsupervised dispute / complaint filing
- Live bureau soft-pull without compliance gates
- Cross-tenant marketplace / product fork
- Unsupported score or legal promises

## Sprint loop

Same as V1.1: sync `main` → one slice → verify → PR → `gh pr merge --auto --squash` → next.
