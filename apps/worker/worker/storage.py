"""MinIO document storage for worker jobs."""

from typing import cast

from minio import Minio

from worker.config import get_worker_settings


class WorkerDocumentStorage:
    def __init__(self) -> None:
        settings = get_worker_settings()
        self._bucket = settings.minio_bucket
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def get_object(self, key: str) -> bytes:
        response = self._client.get_object(self._bucket, key)
        try:
            return cast(bytes, response.read())
        finally:
            response.close()
            response.release_conn()


_storage: WorkerDocumentStorage | None = None


def get_document_storage() -> WorkerDocumentStorage:
    global _storage
    if _storage is None:
        _storage = WorkerDocumentStorage()
    return _storage
