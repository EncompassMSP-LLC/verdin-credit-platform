# End-to-End Workflow Suite

Black-box tests that validate the **platform working as one system** against a running API + worker stack.

Primary golden path (`test_full_case_lifecycle.py`):

```
Organization → User → Authenticate → Case → Account → Document Upload
→ OCR → Classification → Metadata → Entity Resolution → Timeline
→ Task → Mission Control dashboard
```

The organization and owner user are seeded directly in the database (there is
no public sign-up endpoint); **every other step runs through the HTTP API**,
and the asynchronous document pipeline is processed by the **real worker**.

## Tests on disk

| File                                  | Purpose                                      |
| ------------------------------------- | -------------------------------------------- |
| `test_full_case_lifecycle.py`         | 11-stage case + document pipeline happy path |
| `test_dispute_letter_lifecycle.py`    | Dispute draft → review → approve → send      |
| `test_import_to_dispute_lifecycle.py` | Import through dispute letter outcome        |

Keep `test_full_case_lifecycle.py` as the fast, deterministic golden path.
Additional edge cases should be **separate** tests so CI failures stay isolated.

## Layout

```
tests/e2e/
  conftest.py                 # API reachability, DB bootstrap, HTTP client, artifacts
  test_dispute_letter_lifecycle.py
  test_import_to_dispute_lifecycle.py
  test_full_case_lifecycle.py
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

```bash
docker compose up -d postgres redis minio api worker
docker compose exec api alembic upgrade head
```

## Running locally

```bash
# from the repository root, in the API's Python environment
pip install -r apps/api/requirements.txt -r tests/e2e/requirements.txt

# PowerShell example:
$env:E2E_BASE_URL="http://localhost:8000"
$env:DATABASE_URL_SYNC="postgresql://verdin:verdin@localhost:5432/verdin_credit_test"
$env:E2E_REQUIRE="1"

pytest tests/e2e -v
```

If the API is not reachable the suite **skips** locally. Set `E2E_REQUIRE=1`
(as CI does) to make an unreachable stack a hard failure.

Use the **test** database (`verdin_credit_test`) for seeding so you do not wipe local demo data in `verdin_credit`.

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
suite. It is a **required status check** for merges into `main`.
