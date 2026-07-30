#!/usr/bin/env bash
# Restore PostgreSQL and MinIO from a backup created by backup-production.sh.
# DESTRUCTIVE — requires explicit confirmation.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.production.yml}"
COMPOSE=(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE")
BACKUP_DIR="${1:-}"

usage() {
  echo "Usage: $0 <backup-directory>"
  echo "  Example: $0 backups/20260730T120000Z"
  exit 1
}

[[ -n "$BACKUP_DIR" ]] || usage
[[ -d "$BACKUP_DIR" ]] || { echo "Backup directory not found: $BACKUP_DIR" >&2; exit 1; }
[[ -f "$BACKUP_DIR/postgres.sql.gz" ]] || { echo "Missing postgres.sql.gz" >&2; exit 1; }
[[ -f "$BACKUP_DIR/minio-data.tar.gz" ]] || { echo "Missing minio-data.tar.gz" >&2; exit 1; }
[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE" >&2; exit 1; }

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo "WARNING: This will OVERWRITE the staging PostgreSQL database and MinIO object store."
echo "  Backup: $BACKUP_DIR"
echo "  Host:   ${APP_HOSTNAME:-unknown}"
echo "  DB:     ${POSTGRES_DB}"
read -r -p "Type RESTORE-STAGING to continue: " confirm
[[ "$confirm" == "RESTORE-STAGING" ]] || { echo "Aborted."; exit 1; }

echo "==> Stopping application services"
"${COMPOSE[@]}" stop api worker web caddy || true

echo "==> Ensuring postgres + minio are up"
"${COMPOSE[@]}" up -d postgres minio
sleep 5

echo "==> Restoring PostgreSQL"
gunzip -c "$BACKUP_DIR/postgres.sql.gz" \
  | "${COMPOSE[@]}" exec -T postgres \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "==> Restoring MinIO data"
minio_cid="$("${COMPOSE[@]}" ps -q minio)"
"${COMPOSE[@]}" stop minio
docker run --rm \
  --volumes-from "$minio_cid" \
  -v "$(cd "$BACKUP_DIR" && pwd):/backup:ro" \
  alpine:3.20 \
  sh -c 'rm -rf /data/* /data/.[!.]* 2>/dev/null; tar xzf /backup/minio-data.tar.gz -C /data'
"${COMPOSE[@]}" up -d minio

echo "==> Restarting application stack"
"${COMPOSE[@]}" up -d api worker web caddy

echo "Restore complete. Verify https://${APP_HOSTNAME}/api/v1/health/ready"
echo "Reminder: staging must remain demo/synthetic data only."
