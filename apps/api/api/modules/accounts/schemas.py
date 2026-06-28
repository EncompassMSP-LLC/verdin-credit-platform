"""Accounts domain schemas."""

import uuid
from datetime import datetime

from api.core.responses import BaseSchema


class AccountResponse(BaseSchema):
    id: uuid.UUID
    name: str
    account_number: str | None
    email: str | None
    phone: str | None
    organization_id: uuid.UUID
    created_at: datetime
