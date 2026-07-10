#!/usr/bin/env bash
# Deploy Verdin Credit Platform to a single VM using Docker Compose (production pilot).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy .env.production.example and configure secrets first."
  exit 1
fi

if grep -q "replace-with-openssl-rand-hex-32" "$ENV_FILE"; then
  echo "Update SECRET_KEY in $ENV_FILE before deploying."
  exit 1
fi

echo "Building and starting production stack..."
docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" up -d --build

echo "Waiting for API readiness..."
for _ in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" exec -T api \
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/ready')"; then
    echo "API is ready."
    break
  fi
  sleep 5
done

echo ""
echo "Deployment complete."
echo "  App:    http://$(hostname -f 2>/dev/null || echo localhost):${HTTP_PORT:-80}"
echo "  Health: /api/v1/health"
echo "  Ready:  /api/v1/health/ready"
echo ""
echo "Next steps:"
echo "  1. Terminate TLS at nginx or a reverse proxy (see docs/deployment/production.md)"
echo "  2. Create the first organization admin (do NOT run scripts/seed.py in production)"
echo "  3. Configure backups for postgres_data and minio_data volumes"
