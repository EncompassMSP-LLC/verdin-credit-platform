"""Documents domain module."""

from api.modules.documents.models import Document
from api.modules.documents.schemas import DocumentResponse

__all__ = ["Document", "DocumentResponse"]
