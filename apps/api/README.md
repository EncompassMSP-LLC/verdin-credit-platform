# FastAPI API (`apps/api`)

Backend for Ultimate Credit Repair LLC: JWT auth, RBAC, domain modules (cases, accounts, documents, disputes, reporting, compliance, …).

## Run (Docker)

```bash
# from repo root
docker compose up -d api
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
```

API: http://localhost:8000 · Docs: http://localhost:8000/docs

Compose loads repo-root `.env` via `env_file` for `ENABLE_*` flags, then overrides DB/Redis/MinIO to Docker service hostnames. The root `.env` is also mounted at `/app/.env` for pydantic-settings.

## Run (host)

```bash
cd apps/api
pip install -r requirements.txt
# Ensure DATABASE_URL points at localhost Postgres
uvicorn main:app --reload --port 8000
```

## Tests

```bash
cd apps/api
# PowerShell
$env:DATABASE_URL="postgresql+asyncpg://verdin:verdin@localhost:5432/verdin_credit_test"
python -m pytest
```

## Layout

```
api/
  core/          # config, security, permissions, feature_flags, …
  modules/       # domain routers/services/repositories
  models/        # shared model imports as needed
main.py
alembic/
scripts/
tests/
```

Layering: **Router → Service → Repository → Database**.

## Related

- [Developer guide](../../docs/developer-guide.md)
- [API reference](../../docs/api/reference.md)
- [Feature flags](api/core/feature_flags.py)
