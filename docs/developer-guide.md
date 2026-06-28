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
5. Register router in `api/modules/__init__.py`
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
