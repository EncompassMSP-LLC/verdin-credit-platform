#!/usr/bin/env bash
# Validate .env.production for DigitalOcean staging (no unsafe defaults).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker-compose.production.yml}"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

warn() {
  echo "WARNING: $*" >&2
}

[[ -f "$ENV_FILE" ]] || fail "Missing $ENV_FILE — copy .env.production.example and fill secrets."
[[ -f "$COMPOSE_FILE" ]] || fail "Missing $COMPOSE_FILE"

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

required_vars=(
  APP_ENV
  APP_HOSTNAME
  PUBLIC_APP_URL
  CORS_ORIGINS
  CADDY_ACME_EMAIL
  SECRET_KEY
  POSTGRES_USER
  POSTGRES_PASSWORD
  POSTGRES_DB
  DATABASE_URL
  DATABASE_URL_SYNC
  REDIS_URL
  MINIO_ROOT_USER
  MINIO_ROOT_PASSWORD
  MINIO_ACCESS_KEY
  MINIO_SECRET_KEY
)

for var in "${required_vars[@]}"; do
  [[ -n "${!var:-}" ]] || fail "$var is required in $ENV_FILE"
done

[[ "${#SECRET_KEY}" -ge 32 ]] || fail "SECRET_KEY must be at least 32 characters"
[[ "$SECRET_KEY" != *"REPLACE"* ]] || fail "SECRET_KEY still contains REPLACE placeholder"
[[ "$SECRET_KEY" != *"change-me"* ]] || fail "SECRET_KEY must not contain change-me"
[[ "$SECRET_KEY" != "dev-secret-key-change-in-production-32chars" ]] || fail "SECRET_KEY must not use the development default"

[[ "$POSTGRES_PASSWORD" != *"REPLACE"* ]] || fail "POSTGRES_PASSWORD still contains REPLACE placeholder"
[[ "$POSTGRES_PASSWORD" != "verdin" ]] || fail "POSTGRES_PASSWORD must not be the development default"
[[ "${#POSTGRES_PASSWORD}" -ge 12 ]] || fail "POSTGRES_PASSWORD must be at least 12 characters"

[[ "$MINIO_ROOT_PASSWORD" != *"REPLACE"* ]] || fail "MINIO_ROOT_PASSWORD still contains REPLACE placeholder"
[[ "$MINIO_ROOT_PASSWORD" != "minioadmin" ]] || fail "MINIO credentials must not use minioadmin"
[[ "$MINIO_SECRET_KEY" != "minioadmin" ]] || fail "MINIO_SECRET_KEY must not use minioadmin"
[[ "${#MINIO_ROOT_PASSWORD}" -ge 12 ]] || fail "MINIO_ROOT_PASSWORD must be at least 12 characters"

[[ "$APP_HOSTNAME" != *"example.com"* ]] || fail "APP_HOSTNAME must be your real staging hostname (not example.com)"
[[ "$PUBLIC_APP_URL" == https://* ]] || fail "PUBLIC_APP_URL must use https://"
[[ "$CORS_ORIGINS" == https://* ]] || fail "CORS_ORIGINS must use https://"

case "$APP_ENV" in
  staging|production) ;;
  *) fail "APP_ENV must be staging or production (got: $APP_ENV)" ;;
esac

# Staging data policy reminders
if [[ "${ENABLE_CLIENT_PORTAL:-}" != "true" ]]; then
  warn "ENABLE_CLIENT_PORTAL is not true — staging expects the client portal enabled"
fi
if [[ "${ENABLE_AI:-false}" == "true" ]] || [[ "${ENABLE_LLM:-false}" == "true" ]]; then
  warn "AI/LLM flags are enabled — unfinished AI features should stay off unless intentionally testing"
fi
if [[ "${ENABLE_ENTERPRISE:-false}" == "true" ]]; then
  warn "ENABLE_ENTERPRISE is true — unfinished enterprise surfaces should stay off by default"
fi

echo "Validating compose file..."
# Prefer file values over ambient shell env (CI / local developer shells).
rendered="$(
  env -i PATH="$PATH" HOME="$HOME" \
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config
)"

echo "$rendered" >/dev/null

# Only Caddy may publish host ports (80/443).
published_ports="$(echo "$rendered" | awk '/published:/ {print $2}' | tr -d '"')"
while IFS= read -r port; do
  [[ -z "$port" ]] && continue
  case "$port" in
    80|443) ;;
    *) fail "Internal service must not publish host port $port (only 80/443 allowed)" ;;
  esac
done <<<"$published_ports"

echo "OK: $ENV_FILE and $COMPOSE_FILE look safe for staging deploy."
echo "Reminder: staging/demo data only — no real credit reports, SSNs, identity docs, or production PII."
