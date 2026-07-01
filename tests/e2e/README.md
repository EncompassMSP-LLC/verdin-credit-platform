# End-to-End Workflow Suite

A single black-box test that validates the **entire platform working as one
system** — the Sprint 4.3.1 release gate.

```
Organization → User → Authenticate → Case → Account → Document Upload
→ OCR → Classification → Metadata → Entity Resolution → Timeline
→ Task → Mission Control dashboard
```

The organization and owner user are seeded directly in the database (there is
no public sign-up endpoint); **every other step runs through the HTTP API**,
and the asynchronous document pipeline is processed by the **real worker**.

Keep `test_full_case_lifecycle.py` as the fast, deterministic golden path.
Additional edge cases should be separate tests so CI failures stay isolated:

- `test_import_to_dispute_lifecycle.py` — import through dispute letter outcome (4.5 exit gate)
- `test_dispute_letter_lifecycle.py` — dispute draft through CRA outcome
- `test_entity_resolution_ambiguous.py` — ambiguous match
- `test_entity_resolution_unmatched.py` — no match
- `test_ocr_failure_recovery.py` — OCR retry
- `test_worker_restart.py` — worker resilience

## Layout

```
tests/e2e/
  conftest.py                 # API reachability, DB bootstrap, HTTP client, artifacts
  test_dispute_letter_lifecycle.py # dispute letter API happy path
  test_import_to_dispute_lifecycle.py # import → account → dispute letter path
  test_full_case_lifecycle.py # the 11-stage workflow test
  requirements.txt            # reportlab (PDF fixture); rest comes from apps/api
  fixtures/
    organization.py           # seed an isolated org
    users.py                  # seed an owner user
    documents.py              # synthetic credit-report PDF + expected values
    dispute.py                # dispute letter account payloads
  helpers/
    auth.py                   # login / refresh
    wait_for_worker.py        # poll-until helpers for async pipeline stages
    readiness.py              # poll until API reads are consistent after writes
    dispute_lifecycle.py      # shared dispute letter happy-path steps
    assertions.py             # status assertions that record artifacts
    artifacts.py              # diagnostic capture, flushed on failure
```

## Prerequisites

The suite talks to a **running stack**: PostgreSQL, Redis, MinIO, the **worker**,
and the **API**. Bring them up with Docker Compose:

```bash
docker compose up -d postgres redis minio api worker
docker compose exec api alembic upgrade head
```

## Running locally

```bash
# from the repository root, in the API's Python environment
pip install -r apps/api/requirements.txt -r tests/e2e/requirements.txt

# point at the running API (default shown)
export E2E_BASE_URL=http://localhost:8000
export DATABASE_URL_SYNC=postgresql://verdin:verdin@localhost:5432/verdin_credit

pytest tests/e2e -v
```

If the API is not reachable the suite **skips** locally. Set `E2E_REQUIRE=1`
(as CI does) to make an unreachable stack a hard failure.

## Configuration

| Variable            | Default                        | Purpose                                |
| ------------------- | ------------------------------ | -------------------------------------- |
| `E2E_BASE_URL`      | `http://localhost:8000`        | Base URL of the running API            |
| `DATABASE_URL_SYNC` | local `verdin_credit_test` DSN | DB used to seed the org/user           |
| `E2E_REQUIRE`       | unset                          | When set, unreachable stack fails (CI) |

## Diagnostics

Each stage records its request/response payloads. On failure they are flushed
to `tests/e2e/_artifacts/<test>/artifacts.json`. In CI, service logs
(`api.log`, `worker.log`, `minio.log`) are collected alongside them and
uploaded as the `e2e-artifacts` workflow artifact.

## CI

`.github/workflows/e2e.yml` builds the frontend, provisions Postgres/Redis/MinIO,
runs migrations, starts the worker and API, waits for health, and runs this
suite. Once stable it should be added as a **required status check** for merges
into `main`.
