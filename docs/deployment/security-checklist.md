# Staging Security Checklist (DigitalOcean)

Use before every staging go-live and after material infra changes.

## Network

- [ ] UFW (or cloud firewall) allows **only** 22, 80, 443 inbound
- [ ] Postgres, Redis, MinIO, API, worker, and frontend publish **no** host ports
- [ ] Only Caddy binds 80/443 on the host
- [ ] SSH uses key authentication; password login disabled
- [ ] Fail2ban or equivalent considered for SSH brute-force protection

## Secrets

- [ ] `.env.production` exists only on the server (`chmod 600`)
- [ ] No development defaults (`verdin`/`minioadmin`/dev `SECRET_KEY`)
- [ ] `SECRET_KEY` ≥ 32 chars from `openssl rand`
- [ ] MinIO root credentials ≠ `minioadmin`
- [ ] Stripe keys (if any) are **test mode** only
- [ ] `.env.production` is gitignored and never committed

## TLS / edge

- [ ] `APP_HOSTNAME` DNS points at the droplet
- [ ] Caddy obtains Let's Encrypt certificates successfully
- [ ] `PUBLIC_APP_URL` and `CORS_ORIGINS` use `https://app.<DOMAIN>`
- [ ] Marketing site remains on InfinityFree (separate origin)

## Application

- [ ] `APP_ENV=staging`
- [ ] Client portal enabled
- [ ] AI / LLM / unfinished enterprise flags disabled unless explicitly testing
- [ ] Health endpoints return 200: `/api/v1/health`, `/api/v1/health/ready`
- [ ] Log rotation enabled (`max-size` / `max-file` on compose services)

## Data policy (non-negotiable)

- [ ] **No real credit reports**
- [ ] **No real SSNs / identity documents**
- [ ] **No production PII** exports or restores into staging
- [ ] Demo/synthetic seed data only
- [ ] Operators trained that staging is not a production mirror of borrower records

## Operations

- [ ] `./scripts/validate-production-env.sh` passes
- [ ] Backup script exercised at least once
- [ ] Rollback tag strategy understood (`IMAGE_TAG`)
- [ ] GitHub staging deploy is **manual** (`workflow_dispatch`) only
