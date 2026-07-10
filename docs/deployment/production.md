# Production Deployment — Single VM / VPS (Docker Compose)

This guide deploys a **pilot-ready** Verdin stack on one Linux VM using Docker Compose. It is the recommended first production path before moving to managed cloud services.

**Prerequisites:** Ubuntu 22.04+ or similar, Docker Engine 24+, Docker Compose v2, a domain name (optional but recommended), ports 80/443 open.

## What you get

| Component  | Role                                                                   |
| ---------- | ---------------------------------------------------------------------- |
| `nginx`    | Public edge (port 80) — proxies `/` to web, `/api/` to API             |
| `web`      | Production React build with pilot feature flags baked in at build time |
| `api`      | FastAPI with auto-migrations on startup, 2 uvicorn workers             |
| `worker`   | Background jobs (OCR, notifications, reporting refresh)                |
| `postgres` | Primary database (volume-backed)                                       |
| `redis`    | Job queue + cache                                                      |
| `minio`    | Object storage for documents (volume-backed)                           |

Internal services are **not** exposed on host ports in the production compose file — only nginx is public.

## 1. Prepare the server

```bash
# Install Docker (official docs) then:
sudo usermod -aG docker $USER
newgrp docker

git clone <repo-url>
cd verdin-credit-platform
```

## 2. Configure environment

```bash
cp .env.production.example .env.production

# Generate secrets
openssl rand -hex 32   # → SECRET_KEY
openssl rand -hex 16   # → POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD

# Edit .env.production:
# - SECRET_KEY, POSTGRES_PASSWORD, MINIO_* credentials
# - CORS_ORIGINS and PUBLIC_APP_URL → your domain (https://app.example.com)
# - Pilot flags (defaults enable enterprise + client portal)
```

### Pilot feature flags (recommended)

| Backend                     | Frontend                         | Enables                             |
| --------------------------- | -------------------------------- | ----------------------------------- |
| `ENABLE_ENTERPRISE=true`    | `VITE_ENABLE_ENTERPRISE=true`    | Compliance, reporting, org admin UI |
| `ENABLE_CLIENT_PORTAL=true` | `VITE_ENABLE_CLIENT_PORTAL=true` | Client portal routes                |
| `ENABLE_IMPORTS=true`       | `VITE_ENABLE_IMPORTS=true`       | Credit report import wizard         |
| `ENABLE_AI=true`            | `VITE_ENABLE_AI=true`            | Heuristic AI features               |

Keep **OFF** for pilot: `ENABLE_BUREAU_LIVE_API`, `ENABLE_AUTONOMOUS_BUREAU_FILING`, `ENABLE_AGENT_*`, live Stripe/bureau execution flags.

**Important:** Frontend flags are **build-time**. After changing any `VITE_*` variable, rebuild web:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production build web nginx
docker compose -f docker-compose.prod.yml --env-file .env.production up -d web nginx
```

## 3. Deploy

```bash
chmod +x infrastructure/scripts/production-deploy.sh
./infrastructure/scripts/production-deploy.sh
```

Or manually:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Migrations run automatically when the API container starts (`production-api-entrypoint.sh`). Set `SKIP_DB_MIGRATIONS=true` only if you manage migrations externally.

## 4. TLS (HTTPS)

The production nginx config listens on HTTP only. Terminate TLS using one of:

### Option A — Caddy or Traefik in front (simplest)

Point Caddy/Traefik at the VM and proxy to `localhost:80`. Caddy obtains Let's Encrypt certificates automatically.

### Option B — Certbot + nginx on the host

Install certbot on the VM, obtain certs for your domain, and mount certificates into a custom nginx config.

### Option C — Cloudflare proxy

Orange-cloud your domain in Cloudflare; origin connects over HTTP on port 80. Enable "Full (strict)" once origin TLS is configured.

After TLS is active, set:

```env
PUBLIC_APP_URL=https://app.example.com
CORS_ORIGINS=https://app.example.com
```

Rebuild `web` if `VITE_API_BASE_URL` changes.

## 5. First admin user

**Do not run `scripts/seed.py` in production** — it creates demo credentials.

Create your organization and owner account through your chosen bootstrap process (direct DB insert, one-time admin script, or future bootstrap CLI). Until a bootstrap tool ships, use a controlled SQL insert or temporary admin registration endpoint behind a VPN.

## 6. Health checks

| Endpoint                   | Use                                                         |
| -------------------------- | ----------------------------------------------------------- |
| `GET /api/v1/health`       | Liveness — process is up                                    |
| `GET /api/v1/health/ready` | Readiness — database + Redis reachable (returns 503 if not) |

```bash
curl -s http://localhost/api/v1/health
curl -s http://localhost/api/v1/health/ready
```

## 7. Backups (required before pilot traffic)

| Data       | Location               | Backup approach                                            |
| ---------- | ---------------------- | ---------------------------------------------------------- |
| PostgreSQL | `postgres_data` volume | `pg_dump` nightly; test restore monthly                    |
| Documents  | `minio_data` volume    | Volume snapshot or `mc mirror` to S3                       |
| Redis      | `redis_data` volume    | Optional — queue is ephemeral; AOF enabled in prod compose |

Example Postgres backup:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U verdin verdin_credit | gzip > verdin-$(date +%F).sql.gz
```

## 8. Updates

```bash
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

API migrations apply on container restart. Review release notes before upgrading across minor versions.

## 9. Monitoring checklist

- [ ] Uptime monitor on `/api/v1/health/ready`
- [ ] Disk alerts on Docker volumes
- [ ] Log shipping from `docker compose logs` (or Loki/Datadog agent on VM)
- [ ] Postgres connection / slow query monitoring

## 10. Known limitations (pilot)

- Single-node — no horizontal API scaling in this compose file
- MinIO on local volume — migrate to S3 for durability at scale
- No WAF/rate limiting at edge (add via Cloudflare or nginx module)
- OpenAPI `/docs` not disabled in production nginx config (restrict by IP or remove for public internet)
- Advanced enterprise flags (5.9–5.13 scaffolds) remain audit-only — keep disabled unless compliance-approved

## Related documents

- [Deployment guide (dev)](guide.md)
- [Platform capability matrix](../governance/capability-matrix.md)
- [Version 5.0+ pilot scope](../governance/version-5.0-plus-scope.md)
- `.env.production.example` — pilot environment template
