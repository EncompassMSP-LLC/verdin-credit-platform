#!/usr/bin/env bash
# Deploy LRP staging stack on DigitalOcean (Docker Compose + Caddy).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.production.yml}"
COMPOSE=(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE")

export ENV_FILE COMPOSE_FILE

echo "==> Validating configuration"
chmod +x scripts/validate-production-env.sh
./scripts/validate-production-env.sh

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo "==> Building images"
"${COMPOSE[@]}" build

echo "==> Starting infrastructure (postgres, redis, minio)"
"${COMPOSE[@]}" up -d postgres redis minio

echo "==> Waiting for infrastructure health"
for service in postgres redis minio; do
  echo "    waiting for $service..."
  for _ in $(seq 1 60); do
    status="$("${COMPOSE[@]}" ps --status running -q "$service" 2>/dev/null || true)"
    health="$("${COMPOSE[@]}" ps --format json "$service" 2>/dev/null | grep -o '"Health":"[^"]*"' | head -1 || true)"
    if [[ -n "$status" ]] && echo "$health" | grep -q 'healthy'; then
      echo "    $service is healthy"
      break
    fi
    # Fallback: docker inspect health
    cid="$("${COMPOSE[@]}" ps -q "$service")"
    if [[ -n "$cid" ]]; then
      h="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid")"
      if [[ "$h" == "healthy" ]]; then
        echo "    $service is healthy"
        break
      fi
    fi
    sleep 5
  done
  cid="$("${COMPOSE[@]}" ps -q "$service")"
  h="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid")"
  [[ "$h" == "healthy" ]] || {
    echo "ERROR: $service did not become healthy (status=$h)" >&2
    "${COMPOSE[@]}" logs --tail=80 "$service" >&2 || true
    exit 1
  }
done

echo "==> Running Alembic migrations"
"${COMPOSE[@]}" run --rm --no-deps \
  -e SKIP_DB_MIGRATIONS=false \
  api \
  alembic upgrade head

echo "==> Starting application services (api, worker, web, caddy)"
"${COMPOSE[@]}" up -d api worker web caddy

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
  echo "ERROR: API readiness check failed" >&2
  "${COMPOSE[@]}" logs --tail=100 api >&2 || true
  exit 1
}

echo "==> Waiting for frontend + worker health"
for service in web worker caddy; do
  echo "    waiting for $service..."
  for _ in $(seq 1 40); do
    cid="$("${COMPOSE[@]}" ps -q "$service")"
    [[ -n "$cid" ]] || { sleep 3; continue; }
    h="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}running{{end}}' "$cid")"
    if [[ "$h" == "healthy" || "$h" == "running" ]]; then
      # require healthy when healthcheck exists
      if [[ "$h" == "healthy" ]] || [[ "$service" == "caddy" && "$h" == "running" ]]; then
        echo "    $service ok ($h)"
        break
      fi
    fi
    sleep 5
  done
done

echo "==> Post-deploy smoke tests"
smoke_fail=0
"${COMPOSE[@]}" exec -T api \
  python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" \
  || smoke_fail=1
"${COMPOSE[@]}" exec -T api \
  python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/ready')" \
  || smoke_fail=1
"${COMPOSE[@]}" exec -T web wget -qO- http://localhost/ >/dev/null || smoke_fail=1
"${COMPOSE[@]}" exec -T worker \
  python -c "import os, redis; redis.from_url(os.environ['REDIS_URL']).ping()" \
  || smoke_fail=1

# Confirm no data-plane ports on host
if ss -lnt 2>/dev/null | grep -Eq ':(5432|6379|9000|9001|8000)\s'; then
  echo "ERROR: Internal service port appears bound on the host" >&2
  ss -lnt | grep -E ':(5432|6379|9000|9001|8000)\s' >&2 || true
  smoke_fail=1
fi

[[ "$smoke_fail" -eq 0 ]] || {
  echo "ERROR: smoke tests failed" >&2
  exit 1
}

echo ""
echo "Deployment succeeded."
echo "  App:    https://${APP_HOSTNAME}"
echo "  Health: https://${APP_HOSTNAME}/api/v1/health"
echo "  Ready:  https://${APP_HOSTNAME}/api/v1/health/ready"
echo ""
echo "Staging policy: demo/synthetic data only — never real credit reports, SSNs, or production PII."
