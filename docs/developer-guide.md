# Developer Guide

## Quick Start

```bash
# Install Node dependencies
pnpm install

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

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Common Tasks

### Create a new API endpoint

1. Add Pydantic schema in `api/schemas/`
2. Add repository method in `api/repositories/`
3. Add service method in `api/services/`
4. Add router endpoint in `api/routers/`
5. Register router in `api/routers/__init__.py`
6. Write tests in `tests/`
7. Update `docs/api/reference.md`

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
cd apps/api && pytest         # Python tests
```
