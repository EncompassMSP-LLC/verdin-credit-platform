# Race Conditions

**Purpose:** record concurrency and ordering issues discovered during stabilization so future automation work avoids repeating them.

## Document OCR Enqueue Before Commit

**Status:** Fixed during Sprint 4.3.1 E2E stabilization.

### Symptom

Repeated E2E runs sometimes left uploaded documents stuck in `queued`. Worker logs showed:

```text
"job_type": "ocr", "status": "failed", "message": "Document not found"
```

### Cause

The API enqueued the OCR job before the request transaction committed the document row. A fast or idle worker could dequeue the OCR job on a separate database connection before the document was durable, fail with `Document not found`, and drop the only queued job for that document.

The same class of race can occur between worker stages when one stage enqueues the next before committing its own writes.

### Fix

- Persist and commit the document/version before enqueuing OCR.
- Enqueue OCR → classification → metadata → entity resolution only after each stage commits the data the next stage reads.
- Keep the golden-path E2E workflow as the release gate so regressions in cross-process timing are visible.

### Rule

Any job that reads data written by the current transaction must be enqueued only after that transaction is committed, or through an outbox/job orchestration mechanism that guarantees commit-before-dispatch semantics.

### Future Guardrail

Version 4.5 job orchestration should centralize this pattern so imports, OCR, automation, notifications, and AI jobs do not implement enqueue timing independently.
