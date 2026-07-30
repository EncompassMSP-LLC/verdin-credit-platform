# Staging Rollback

## Application image rollback

Deploy stamps `IMAGE_TAG` with the short git SHA. To roll back containers:

```bash
cd /opt/lrp/app
./scripts/rollback-production.sh <previous-sha>
# Prompt: type ROLLBACK-STAGING
```

This rewrites `IMAGE_TAG` in `.env.production` and recreates `api`, `worker`, `web`, and `caddy`.

## When a DB restore is also required

If the newer release ran Alembic migrations that the older code cannot read:

1. Roll back images **or**
2. Restore a backup taken **before** the migration (`scripts/restore-production.sh`)

Prefer restoring a matching backup over attempting down-revisions in staging unless the migration is explicitly reversible and tested.

## GitHub Actions

Re-run **Staging Deploy (DigitalOcean)** with an earlier `git_ref` (tag or SHA). Confirm with `deploy-staging`.

## After rollback

```bash
curl -fsS "https://app.<DOMAIN>/api/v1/health/ready"
docker compose -f docker-compose.production.yml --env-file .env.production ps
```

Document the incident (what failed, which tag restored, whether DB restore was needed).
