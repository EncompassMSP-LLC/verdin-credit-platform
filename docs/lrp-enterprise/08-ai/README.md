# 08 — AI

AI-assisted credit analysis and narrative features for LRP.

## Code

| Capability                    | Path                                    |
| ----------------------------- | --------------------------------------- |
| Credit analysis orchestration | `apps/api/api/modules/credit_analysis/` |
| LLM gates                     | ADR-012 · `apps/api/api/modules/llm/`   |
| Parsers                       | `packages/report-parsers/`              |

## Guardrails

- Deterministic analysis preferred; LLM only behind ADR-012 + org policy
- No unsupervised dispute filing
- Outputs are advisory for partner handoff
