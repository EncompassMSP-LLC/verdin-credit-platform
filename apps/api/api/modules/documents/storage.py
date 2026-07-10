"""Document object storage abstraction."""

from __future__ import annotations

import asyncio
from io import BytesIO
from typing import Protocol, runtime_checkable

from minio import Minio

from api.core.config import get_settings


@runtime_checkable
class DocumentStorage(Protocol):
    def ensure_bucket(self) -> None: ...

    def put_object(self, key: str, data: bytes, content_type: str) -> None: ...

    def get_object(self, key: str) -> bytes: ...

    def remove_object(self, key: str) -> None: ...


class MinioDocumentStorage:
    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.minio_bucket
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self.ensure_bucket()
        self._client.put_object(
            self._bucket,
            key,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def get_object(self, key: str) -> bytes:
        response = self._client.get_object(self._bucket, key)
        try:
            body: bytes = response.read()
            return body
        finally:
            response.close()
            response.release_conn()

    def remove_object(self, key: str) -> None:
        self._client.remove_object(self._bucket, key)


class MemoryDocumentStorage:
    """In-memory storage for tests."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}

    def ensure_bucket(self) -> None:
        return None

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        del content_type
        self._objects[key] = data

    def get_object(self, key: str) -> bytes:
        if key not in self._objects:
            raise FileNotFoundError(key)
        return self._objects[key]

    def remove_object(self, key: str) -> None:
        self._objects.pop(key, None)


async def async_put(storage: DocumentStorage, key: str, data: bytes, content_type: str) -> None:
    await asyncio.to_thread(storage.put_object, key, data, content_type)


async def async_get(storage: DocumentStorage, key: str) -> bytes:
    return await asyncio.to_thread(storage.get_object, key)


async def async_remove(storage: DocumentStorage, key: str) -> None:
    await asyncio.to_thread(storage.remove_object, key)


_storage: DocumentStorage | None = None


def get_document_storage() -> DocumentStorage:
    global _storage
    if _storage is None:
        _storage = MinioDocumentStorage()
    return _storage


def set_document_storage(storage: DocumentStorage) -> None:
    global _storage
    _storage = storage


def reset_document_storage() -> None:
    global _storage
    _storage = None
