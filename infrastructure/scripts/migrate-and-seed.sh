#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -U verdin; do
  sleep 2
done

echo "Running Alembic migrations..."
cd /app
alembic upgrade head

echo "Seeding database..."
python scripts/seed.py

echo "Database setup complete."
