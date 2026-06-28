"""Cases domain schemas."""

import uuid
from datetime import datetime

from api.core.responses import BaseSchema
from api.modules.cases.models import CaseStatus


class CaseResponse(BaseSchema):
    id: uuid.UUID
    title: str
    description: str | None
    status: CaseStatus
    case_number: str | None
    organization_id: uuid.UUID
    account_id: uuid.UUID | None
    assigned_to_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
