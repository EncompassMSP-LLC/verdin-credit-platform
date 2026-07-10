# Local Docker Pilot

Run a **production-mode** stack on Docker Desktop — no VM, no domain, no HTTPS required. Uses a separate Compose project (`verdin-pilot`) so it does not clash with your dev `docker compose up` database containers.

## Quick start

```powershell
cd c:\Projects\verdin-credit-platform\verdin-credit-platform

# One-time config (or edit secrets if you prefer)
copy .env.production.example .env.production

# Build and start (first run takes several minutes)
docker compose -f docker-compose.local-pilot.yml --env-file .env.production up -d --build
```

Open **http://localhost:8080**

## Verify

```powershell
curl http://localhost:8080/api/v1/health
curl http://localhost:8080/api/v1/health/ready
```

`ready` should return `"status":"ready"` once Postgres and Redis are up. Migrations run automatically when the API starts.

## Demo login (local pilot only)

After the stack is healthy, seed demo users **once**:

```powershell
docker compose -f docker-compose.local-pilot.yml --env-file .env.production exec api python scripts/seed.py
```

| Email             | Password    | Role  |
| ----------------- | ----------- | ----- |
| owner@verdin.demo | changeme123 | Owner |
| admin@verdin.demo | changeme123 | Admin |

Do **not** use `seed.py` on a real production server.

## What's enabled

Pilot flags in `.env.production.example`:

- Enterprise UI (compliance, reporting, org admin)
- Client portal
- Credit report import wizard
- AI heuristics (not LLM unless you set `ENABLE_LLM=true` and provider keys)

## Commands

```powershell
# Logs
docker compose -f docker-compose.local-pilot.yml --env-file .env.production logs -f api

# Stop
docker compose -f docker-compose.local-pilot.yml --env-file .env.production down

# Stop and delete pilot data volumes
docker compose -f docker-compose.local-pilot.yml --env-file .env.production down -v
```

## Dev stack vs local pilot

|               | Dev (`docker-compose.yml`) | Local pilot (`docker-compose.local-pilot.yml`) |
| ------------- | -------------------------- | ---------------------------------------------- |
| API mode      | Hot reload, bind mounts    | Production image, 2 workers                    |
| URL           | http://localhost           | http://localhost:8080                          |
| Project       | default                    | `verdin-pilot` (separate DB volumes)           |
| Feature flags | Mostly off in compose      | Pilot flags on                                 |

You can keep dev Postgres/Redis/MinIO running on ports 5432/6379/9000 — the pilot stack uses internal Docker networks only.

## When you get a server

See [production.md](production.md) for VM deploy with `docker-compose.prod.yml` and TLS.
