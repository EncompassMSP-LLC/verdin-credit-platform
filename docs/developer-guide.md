# Developer Guide

## Quick Start

```bash
# Install Node dependencies
pnpm install

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install

# Set up environment
cp .env.example .env

# Start PostgreSQL and Redis (via Docker)
docker compose up postgres redis -d

# Set up Python virtual environment
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and seed
alembic upgrade head
python scripts/seed.py

# Start API
uvicorn main:app --reload

# In another terminal, start frontend
cd apps/web
pnpm dev
```

## Development URLs

| Service    | URL                        |
| ---------- | -------------------------- |
| Frontend   | http://localhost:5173      |
| API        | http://localhost:8000      |
| API Docs   | http://localhost:8000/docs |
| PostgreSQL | localhost:5432             |

## Common Tasks

### Create a new API endpoint

1. Add Pydantic schema in `api/modules/<domain>/schemas.py`
2. Add repository method in `api/modules/<domain>/repository.py`
3. Add service method in `api/modules/<domain>/service.py`
4. Add router endpoint in `api/modules/<domain>/router.py`
5. Register router in `api/versions/v1/router.py`
6. Write tests in `tests/`
7. Update `docs/api/reference.md`

Reuse shared utilities from `api/core/` (responses, pagination, permissions, security, audit, exceptions).

### Create a database migration

```bash
cd apps/api
alembic revision --autogenerate -m "add_new_table"
alembic upgrade head
```

### Add a shared type

1. Add to `packages/shared/src/index.ts`
2. Run `pnpm --filter @verdin/shared build`
3. Import in frontend: `import { ... } from '@verdin/shared'`

### Run case management locally

```bash
cd apps/api
alembic upgrade head
python scripts/seed.py
uvicorn main:app --reload
```

Use `manager@verdin.demo / changeme123` to create cases and `admin@verdin.demo` to delete.

See `docs/release-notes/sprint-2-epic-1-cases.md` for Sprint 2 Epic 1 details.

### Run account intelligence locally

```bash
cd apps/api
alembic upgrade head   # includes 003_credit_accounts migration
python scripts/seed.py
uvicorn main:app --reload
```

Use `manager@verdin.demo / changeme123` to create accounts and `admin@verdin.demo` to delete.

Frontend routes: `/accounts`, `/accounts/new`, `/accounts/:id`, `/cases/:caseId/accounts`

Intelligence scoring lives in `api/modules/accounts/intelligence.py`. The service recalculates scores on every create/update.

See `docs/sprint-2/account-intelligence.md` for Sprint 2 Epic 2 details.

## Code Quality

```bash
pnpm lint          # ESLint
pnpm typecheck     # TypeScript
pnpm format        # Prettier
cd apps/api && ruff check .   # Python lint
cd apps/api && ruff format .  # Python format
cd apps/api && mypy --config-file=pyproject.toml api main.py  # Python types
cd apps/api && pytest         # Python tests
```

### Pre-commit Hooks

The repository uses [pre-commit](https://pre-commit.com/) to enforce formatting and linting before commits.

**Setup (once per clone):**

```bash
pip install pre-commit
pnpm install
cd apps/api && pip install -r requirements.txt
pre-commit install
```

**Run manually:**

```bash
pre-commit run --all-files
```

**Hooks:**

| Hook          | Tool                        | Files                                  |
| ------------- | --------------------------- | -------------------------------------- |
| `ruff`        | Python lint (with auto-fix) | `apps/api/`, `apps/worker/`            |
| `ruff-format` | Python format               | `apps/api/`, `apps/worker/`            |
| `mypy-api`    | Python type check           | `apps/api/`                            |
| `prettier`    | Frontend & docs format      | `.ts`, `.tsx`, `.json`, `.md`, `.yaml` |
| `eslint`      | Frontend lint               | `.ts`, `.tsx`                          |

ESLint and Prettier hooks require `pnpm install` so `pnpm exec` is available. The mypy hook installs its own Python dependencies in an isolated pre-commit environment.

Configuration: `.pre-commit-config.yaml`

## Feature Flags

Feature flags gate optional platform capabilities. Backend and frontend each read their own environment variables; keep both sides aligned when toggling a feature for end users.

### Available flags

| Flag                   | Description                                  |
| ---------------------- | -------------------------------------------- |
| `ENABLE_AI`            | AI-powered features (summaries, suggestions) |
| `ENABLE_IMPORTS`       | Data import pipeline                         |
| `ENABLE_ENTERPRISE`    | Enterprise-tier capabilities                 |
| `ENABLE_CLIENT_PORTAL` | Client-facing portal                         |

### Backend

Flags are defined in `api/core/feature_flags.py` and loaded from `ENABLE_*` variables in `.env`.

```python
from api.core.feature_flags import FeatureFlag, get_feature_flags, is_feature_enabled

if is_feature_enabled(FeatureFlag.ENABLE_AI):
    ...

flags = get_feature_flags()
if flags.enable_imports:
    ...
```

### Frontend

Flags are exposed via Vite environment variables (`VITE_ENABLE_*`) and accessed through `apps/web/src/lib/feature-flags.ts`.

```typescript
import { featureFlags, isFeatureEnabled } from '@/lib/feature-flags';

if (isFeatureEnabled('ENABLE_CLIENT_PORTAL')) {
  ...
}

if (featureFlags.enableAi) {
  ...
}
```

Set flags in `.env` (see `.env.example`). Restart the dev server after changing Vite variables.

## Background Jobs

The worker (`apps/worker`) processes asynchronous jobs from a Redis queue. Sprint 1 provides the architecture only; job implementations are placeholders until Sprint 2.

### Layout

```
apps/worker/
  main.py                 # Entry point
  worker/
    config.py             # WorkerSettings (Redis URL, queue name, poll interval)
    constants.py          # JobType, JobStatus
    base.py               # BaseJob, JobContext, JobResult
    registry.py           # @register_job decorator and lookup
    queue.py              # enqueue_job / dequeue_job (Redis LPUSH / BRPOP)
    runner.py             # Poll loop and dispatch
    jobs/                 # One module per job type
```

### Registered job types (placeholders)

| JobType          | Module                   | Purpose                      |
| ---------------- | ------------------------ | ---------------------------- |
| `ocr`            | `jobs/ocr.py`            | Document text extraction     |
| `report_import`  | `jobs/report_import.py`  | Bulk credit report ingestion |
| `ai_summary`     | `jobs/ai_summary.py`     | Case/document summarization  |
| `monthly_review` | `jobs/monthly_review.py` | Scheduled portfolio review   |

### Job status values

`pending` → `queued` → `running` → `completed` | `failed` | `cancelled`

Statuses are defined in `worker/constants.py` (`JobStatus`). Sprint 2 will persist status transitions in PostgreSQL; the queue message currently carries an initial `queued` status.

### Running the worker locally

```bash
# Redis must be running
docker compose up redis -d

cd apps/worker
pip install -r requirements.txt
python main.py
```

### Sprint 2: triggering jobs from the API

Jobs will **not** be triggered directly from FastAPI route handlers in Sprint 1. In Sprint 2:

1. **API service layer** validates the request, creates a job record (PostgreSQL), and enqueues work.
2. **Enqueue** pushes a JSON message to Redis list `verdin:jobs` (configurable via `WORKER_QUEUE_NAME`):

   ```json
   {
     "job_id": "uuid",
     "job_type": "ocr",
     "payload": { "document_id": "uuid" },
     "status": "queued"
   }
   ```

3. The API can call the same contract using `redis-py` (mirror `worker/queue.py`) or a shared enqueue helper extracted to a common package.
4. **Worker** blocks on `BRPOP`, resolves `job_type` via `worker/registry.py`, and invokes `BaseJob.run()`.
5. **Status updates** — the worker (or job implementation) writes `running` / `completed` / `failed` back to the job record; the API exposes `GET /api/v1/jobs/{id}` for polling.

Example enqueue (development / tests):

```python
from worker.constants import JobType
from worker.queue import enqueue_job

message = enqueue_job(JobType.OCR, {"document_id": "..."})
```

Feature flags (`ENABLE_AI`, `ENABLE_IMPORTS`) will gate which API endpoints enqueue jobs in Sprint 2.
