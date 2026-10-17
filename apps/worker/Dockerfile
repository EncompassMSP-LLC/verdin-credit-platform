FROM python:3.14-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY apps/worker/requirements.txt .
COPY packages/job-orchestrator /packages/job-orchestrator
COPY packages/llm-gateway /packages/llm-gateway
COPY packages/report-parsers /packages/report-parsers
COPY packages/document-classification /packages/document-classification
COPY packages/document-metadata /packages/document-metadata
COPY packages/entity-resolution /packages/entity-resolution
COPY packages/event-bus /packages/event-bus
COPY packages/event-types /packages/event-types
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/worker .

CMD ["python", "main.py"]
