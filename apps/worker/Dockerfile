FROM python:3.14-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY apps/worker/requirements.txt .
COPY packages/document-metadata packages/document-metadata
COPY packages/entity-resolution packages/entity-resolution
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/worker .

CMD ["python", "main.py"]
