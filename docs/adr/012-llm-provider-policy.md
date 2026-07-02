# ADR-012: LLM Provider Policy and Feature Gates

**Date:** 2026-07-01  
**Authors:** Platform Team

## Status

Accepted

## Context

Version 4.5 deferred all external LLM calls (case summaries, document summaries, dispute draft augmentation) pending provider selection and PII policy approval. Version 4.8 requires a formal gate before any production code invokes third-party LLM APIs.

Requirements:

- Separate **heuristic/rules AI** (`ENABLE_AI`) from **external LLM calls** (`ENABLE_LLM`)
- Provider credentials and model configuration via environment variables — never in code
- Default-deny PII export to external providers unless `LLM_ALLOW_EXTERNAL_PII_EXPORT=true`
- Scrubbing helpers for prompts assembled from case/document context
- Readiness endpoint for staff to verify configuration without calling providers
- No external LLM network calls in CI

Alternatives considered:

- Reuse `ENABLE_AI` for LLM — rejected; heuristics must remain available when LLM is off
- Per-organization provider config in PostgreSQL — deferred to 5.0 enterprise admin
- Immediate OpenAI integration in this slice — rejected; policy and gates must land first (checklist slice 8)

## Decision

Introduce **`packages/llm-gateway/`** (`verdin-llm-gateway`) with:

| Module          | Responsibility                                             |
| --------------- | ---------------------------------------------------------- |
| `config.py`     | `LlmGatewaySettings` — `LLM_PROVIDER`, `LLM_API_KEY`, etc. |
| `policy.py`     | PII field denylist, `redact_pii()`, `scrub_payload()`      |
| `gate.py`       | `evaluate_llm_gate()`, `require_llm_ready()`               |
| `exceptions.py` | Typed errors for disabled feature, missing config, PII     |

**Feature flag:** `ENABLE_LLM` (default `false`) — independent of `ENABLE_AI`.

**API surface:**

- `GET /api/v1/llm/status` — authenticated staff readiness check (no provider call)
- `api.core.llm.require_llm_gateway()` — call from services/workers before any future LLM invocation

**Provider env vars:**

| Variable                        | Purpose                                       |
| ------------------------------- | --------------------------------------------- |
| `LLM_PROVIDER`                  | `none`, `openai`, `azure_openai`, `anthropic` |
| `LLM_API_KEY`                   | Provider API key                              |
| `LLM_MODEL`                     | Default model id                              |
| `LLM_BASE_URL`                  | Required for Azure/custom hosts               |
| `LLM_ALLOW_EXTERNAL_PII_EXPORT` | Explicit PII opt-in (default false)           |
| `LLM_TIMEOUT_SECONDS`           | Request timeout (default 30)                  |

**Implementation rules for follow-up slices (9+):**

1. Call `require_llm_gateway()` before any external request
2. Pass assembled context through `scrub_payload()` unless `requires_pii_export=True` and opt-in is set
3. Record model id, prompt hash, and timestamp on timeline/audit when LLM output is persisted
4. Never call providers from routers; services or worker jobs only
5. Mock providers in tests — no network in CI

## Consequences

### Positive

- Clear compliance gate before LLM features ship
- Heuristic intelligence continues under `ENABLE_AI` without provider keys
- Shared package usable from API and worker
- Staff can verify readiness via `/llm/status`

### Negative

- Provider config is global per deployment until per-org settings land in 5.0
- PII scrubbing is best-effort regex/field denylist — not a substitute for legal review
- No actual LLM client in this slice — follow-up work still required for summaries

### Neutral

- See [`docs/architecture/ai-architecture.md`](../architecture/ai-architecture.md) for integration pattern
- Capability matrix row **LLM Policy Gates** tracks scaffold vs full LLM features
