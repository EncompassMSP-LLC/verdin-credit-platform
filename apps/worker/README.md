# Worker (`apps/worker`)

Background job consumer for OCR, classification, metadata, entity resolution, credit-report parse, notifications, and other async work.

Uses Redis queue (`WORKER_QUEUE_NAME`, default `verdin:jobs`) via `packages/job-orchestrator`.

## Run (Docker)

```bash
docker compose up -d worker
docker compose logs -f worker
```

Worker shares MinIO/Postgres settings with the API. Rebuild after changing `packages/report-parsers` or worker code:

```bash
docker compose build worker
docker compose up -d worker
```

## Run (host)

```bash
cd apps/worker
pip install -r requirements.txt
# REDIS_URL / DATABASE_URL_SYNC / MINIO_* from environment or repo-root .env
python main.py
```

## Related

- [`packages/job-orchestrator`](../../packages/job-orchestrator/)
- [`packages/report-parsers`](../../packages/report-parsers/README.md)
- [Developer guide](../../docs/developer-guide.md)
