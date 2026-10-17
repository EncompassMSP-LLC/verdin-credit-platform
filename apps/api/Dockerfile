FROM python:3.14-slim AS base

WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
COPY packages/llm-gateway /packages/llm-gateway
COPY packages/job-orchestrator /packages/job-orchestrator
COPY packages/document-classification /packages/document-classification
COPY packages/document-metadata /packages/document-metadata
COPY packages/entity-resolution /packages/entity-resolution
COPY packages/event-bus /packages/event-bus
COPY packages/event-types /packages/event-types
COPY packages/report-parsers /packages/report-parsers
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api .

EXPOSE 8000

FROM base AS development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
RUN printf '%s\n' \
    '#!/bin/sh' \
    'set -e' \
    'if [ "${SKIP_DB_MIGRATIONS:-false}" != "true" ]; then' \
    '  echo "Running database migrations..."' \
    '  alembic upgrade head' \
    'fi' \
    'echo "Starting API server..."' \
    'exec "$@"' \
    > /entrypoint.sh && chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
