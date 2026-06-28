"""Documents domain schemas."""

import uuid
from datetime import datetime

from api.core.responses import BaseSchema


class DocumentResponse(BaseSchema):
    id: uuid.UUID
    title: str
    file_name: str
    mime_type: str | None
    file_size: int | None
    case_id: uuid.UUID
    created_at: datetime
