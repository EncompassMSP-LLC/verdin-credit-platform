#!/usr/bin/env bash
# Roll back staging containers to a previous image tag and re-run migrations if needed.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.production.yml}"
TARGET_TAG="${1:-}"

usage() {
  echo "Usage: $0 <image-tag>"
  echo "  Rolls api/worker/web images back to IMAGE_TAG=<tag> and restarts the stack."
  echo "  Example: $0 abcdef12"
  exit 1
}

[[ -n "$TARGET_TAG" ]] || usage
[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE" >&2; exit 1; }

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo "WARNING: Rolling back application images to tag: $TARGET_TAG"
read -r -p "Type ROLLBACK-STAGING to continue: " confirm
[[ "$confirm" == "ROLLBACK-STAGING" ]] || { echo "Aborted."; exit 1; }

# Persist tag for subsequent compose operations
if grep -q '^IMAGE_TAG=' "$ENV_FILE"; then
  sed -i.bak "s/^IMAGE_TAG=.*/IMAGE_TAG=${TARGET_TAG}/" "$ENV_FILE"
  rm -f "${ENV_FILE}.bak"
else
  echo "IMAGE_TAG=${TARGET_TAG}" >>"$ENV_FILE"
fi

COMPOSE=(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE")

echo "==> Recreating api, worker, web with IMAGE_TAG=$TARGET_TAG"
"${COMPOSE[@]}" up -d --no-build api worker web caddy

echo "==> Waiting for API readiness"
ready=0
for _ in $(seq 1 40); do
  if "${COMPOSE[@]}" exec -T api \
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/ready')"; then
    ready=1
    break
  fi
  sleep 5
done
[[ "$ready" -eq 1 ]] || {
  echo "ERROR: API not ready after rollback" >&2
  "${COMPOSE[@]}" logs --tail=80 api >&2 || true
  exit 1
}

echo "Rollback complete to IMAGE_TAG=$TARGET_TAG"
echo "If schema is ahead of the rolled-back code, restore a matching DB backup (see docs/deployment/rollback.md)."
