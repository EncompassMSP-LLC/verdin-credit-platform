FROM python:3.13-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
COPY packages/document-classification /packages/document-classification
COPY packages/document-metadata /packages/document-metadata
COPY packages/entity-resolution /packages/entity-resolution
COPY packages/event-bus /packages/event-bus
COPY packages/event-types /packages/event-types
COPY packages/report-parsers /packages/report-parsers
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
