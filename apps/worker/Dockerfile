FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY packages/document-classification /packages/document-classification
COPY apps/worker/requirements.txt .
RUN pip install --no-cache-dir /packages/document-classification \
    && pip install --no-cache-dir -r requirements.txt

COPY apps/worker/ .

CMD ["python", "main.py"]
