#!/usr/bin/env bash
# Backup PostgreSQL and MinIO volumes for LRP staging.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.production.yml}"
COMPOSE=(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE")
BACKUP_ROOT="${BACKUP_ROOT:-$ROOT_DIR/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$BACKUP_ROOT/$STAMP"

[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE" >&2; exit 1; }

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

mkdir -p "$DEST"

echo "==> PostgreSQL dump → $DEST/postgres.sql.gz"
"${COMPOSE[@]}" exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  | gzip -c >"$DEST/postgres.sql.gz"

echo "==> MinIO data archive → $DEST/minio-data.tar.gz"
minio_cid="$("${COMPOSE[@]}" ps -q minio)"
[[ -n "$minio_cid" ]] || { echo "MinIO container not running" >&2; exit 1; }
docker run --rm \
  --volumes-from "$minio_cid" \
  -v "$DEST:/backup" \
  alpine:3.20 \
  tar czf /backup/minio-data.tar.gz -C /data .

cat >"$DEST/manifest.txt" <<EOF
created_at_utc=$STAMP
app_hostname=${APP_HOSTNAME:-unknown}
postgres_db=${POSTGRES_DB}
minio_bucket=${MINIO_BUCKET:-verdin-documents}
compose_file=$COMPOSE_FILE
EOF

echo "Backup complete: $DEST"
echo "Retain off-droplet copies of backups for disaster recovery."
