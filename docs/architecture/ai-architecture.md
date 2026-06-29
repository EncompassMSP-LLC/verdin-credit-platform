# AI Architecture

How artificial intelligence and machine learning capabilities integrate into the Verdin platform across Phases 1–4 of the [Version 5.0 roadmap](../roadmap/v5.0-enterprise.md#ai-roadmap).

## Design principles

1. **AI augments operators** — humans approve disputes, letters, and client communications
2. **Structured inputs** — models consume typed domain objects (Case, Account, Document), not raw DB rows
3. **Async by default** — OCR, summarization, and batch scoring run in the worker queue
4. **Explainable outputs** — store rationale text (`ai_summary`, `ai_recommended_next_action`) alongside scores
5. **Feature-flagged** — `ENABLE_AI` gates AI endpoints and job enqueue ([developer guide](../developer-guide.md))

## AI capability layers

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation — AI insights in web UI, client portal (4.8)   │
├─────────────────────────────────────────────────────────────┤
│  API — intelligence endpoints, summary fields on entities    │
├─────────────────────────────────────────────────────────────┤
│  Service — heuristics + model invocation, prompt assembly    │
├─────────────────────────────────────────────────────────────┤
│  Worker — OCR, classification, batch inference (4.5+)      │
├─────────────────────────────────────────────────────────────┤
│  Data — documents (MinIO), embeddings store (5.0 TBD)        │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1 — Document intelligence (target 4.5)

| Capability              | Flow                                                                       |
| ----------------------- | -------------------------------------------------------------------------- |
| **OCR**                 | Document uploaded → worker job → extract text → store in document metadata |
| **Classification**      | Model assigns type (credit report, ID, correspondence)                     |
| **Metadata extraction** | Parse bureau, date, consumer name from credit reports                      |
| **Entity recognition**  | Map tradelines to Account create/update suggestions                        |

**Job pattern:** `BaseJob` in `apps/worker` → idempotent → update Document status → emit TimelineEvent.

## Phase 2 — Operational AI (target 4.5–4.8)

| Capability                     | Current / planned                                                     |
| ------------------------------ | --------------------------------------------------------------------- |
| **Case summaries**             | Field on Case (`summary` manual today; AI-generated 4.5)              |
| **Account recommendations**    | `ai_recommended_next_action` on Account ✅ (heuristic today; LLM 4.5) |
| **Risk / readiness scores**    | `apply_account_intelligence()` ✅ heuristic; ML calibration 5.0       |
| **Dispute suggestions**        | Dispute Generation Engine templates + AI draft (4.5)                  |
| **Missing evidence detection** | Compare case documents vs account dispute requirements (4.8)          |

### Heuristic intelligence (shipped — Sprint 2 Epic 2)

Location: `api/modules/accounts/intelligence.py`

- `calculate_risk_score()` — payment status, account status, past due
- `calculate_readiness_score()` — dispute status, evidence completeness, cooldown
- `calculate_dispute_status()` — evidence gates and active dispute preservation
- `recommend_next_action()` — rule-based next step text

These functions are the **fallback and baseline** when AI is disabled or unavailable.

## Phase 3 — Orchestration (target 5.0)

- **Workflow triggers** — AI evaluates case state → enqueues tasks or workflow steps
- **Predictive outcomes** — dispute success probability, time-to-resolution estimates
- **Intelligent prioritization** — rank cases/accounts for analyst queues

Architecture: event-driven — TimelineEvent or workflow signal → AI evaluator worker → proposed actions stored for human approval.

## Phase 4 — Autonomous preparation (5.0+)

- Autonomous case preparation (with compliance guardrails)
- Automated dispute letter generation and mailing integration
- Continuous bureau monitoring and re-dispute scheduling

Requires: Compliance Center, consent verification, human approval gates, full audit immutability.

## Model integration pattern (4.5+)

```python
# Service layer — pseudo-code
async def generate_case_summary(self, case_id: UUID) -> str:
    if not settings.ENABLE_AI:
        raise FeatureDisabledError()
    context = await self._build_case_context(case_id)  # Case + accounts + docs metadata
    result = await self._ai_client.complete(prompt=CASE_SUMMARY_PROMPT, context=context)
    await self._timeline.emit(case_id, "ai_summary_generated", ...)
    return result.text
```

**Rules:**

- Never call external LLM APIs from routers
- Log prompt hash and model version for audit (5.0)
- Redact PII per org policy before sending to third-party models
- Timeout and circuit-breaker on AI provider calls

## Storage for AI artifacts

| Artifact              | Storage                                 |
| --------------------- | --------------------------------------- |
| OCR text              | Document metadata JSON or child table   |
| Summary text          | Entity fields (`ai_summary`, `summary`) |
| Embeddings (5.0)      | pgvector or dedicated vector store      |
| Prompt/response audit | Compliance audit store (5.0)            |

## Worker jobs (AI-related)

| Job                   | Version | Module                                    |
| --------------------- | ------- | ----------------------------------------- |
| `ai_summary`          | 4.5     | `worker/jobs/ai_summary.py` (placeholder) |
| `document_ocr`        | 4.5     | planned                                   |
| `document_classify`   | 4.5     | planned                                   |
| `import_parse_report` | 4.5     | planned                                   |

See [ADR 008 — Background jobs](../adr/008-background-jobs.md).

## Testing AI features

- Unit test heuristics with fixed inputs (no network)
- Integration tests mock AI provider responses
- Golden-file tests for prompt templates
- Do not call production LLM APIs in CI

## Related documents

- [Credit Account Intelligence — Sprint 2](../sprint-2/account-intelligence.md)
- [Domain Model — Account aggregate](domain-model.md#credit-account-intelligence-implemented)
- [Security Architecture — PII handling](security-architecture.md#encryption)
