#!/bin/sh
set -e

if [ "${SKIP_DB_MIGRATIONS:-false}" != "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

echo "Starting API server..."
exec "$@"
