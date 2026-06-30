# Coverage Plan

**Purpose:** increase confidence in high-risk platform workflows instead of chasing raw coverage percentages.

Security review should run before major coverage expansion because security findings may change what tests need to enforce.

## Priority Areas

| Area                              | Why It Matters                                        | Status   |
| --------------------------------- | ----------------------------------------------------- | -------- |
| Event bus publishing/subscribing  | Timeline, tasks, and dashboards depend on event flow. | Complete |
| Worker retry and failure recovery | OCR and document intelligence depend on async jobs.   | Complete |
| Dashboard aggregation             | Mission Control is the operational source of truth.   | Complete |
| Entity resolution ambiguity       | Incorrect linkage can corrupt operational context.    | Complete |
| Timeline event sequencing         | Auditability depends on complete, ordered events.     | Complete |
| RBAC denial paths                 | Security review findings should be enforced in tests. | Complete |

## Sprint 4.3.1 Evidence

- Event bus: `tests/timeline/test_event_bus.py` covers async dispatch, sync dispatch, unsubscribe, and global bus isolation.
- Worker failure recovery: `apps/worker/tests/test_runner.py` covers dispatch exception containment; document retry remains exposed through `POST /documents/{id}/ocr/retry`.
- Dashboard aggregation: `tests/dashboard/test_dashboard_api.py` covers cases, accounts, tasks, timeline, alerts, and read-only access.
- Entity resolution ambiguity: `tests/documents/test_entity_resolution.py` covers matched, ambiguous, and unmatched account outcomes.
- Timeline sequencing: `tests/timeline/test_timeline_endpoints.py` verifies ordered case lifecycle events.
- RBAC denial paths: case/account/task/document/security tests cover unauthenticated access, read-only write denial, manager admin denial, and token rejection.

## Test Shape

Prefer focused tests that isolate a risk:

- One assertion family per test file.
- Clear fixture setup.
- Explicit expected timeline/events.
- Artifact output for async failures when practical.

## Non-Goals

- Increasing coverage for simple CRUD handlers just to raise a percentage.
- Expanding the golden-path E2E test with unrelated edge cases.
- Adding broad, slow tests before security review clarifies expected behavior.
