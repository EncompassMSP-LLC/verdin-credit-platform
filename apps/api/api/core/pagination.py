"""Pagination utilities and response models."""

import math

from pydantic import Field

from api.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from api.core.responses import BaseSchema


class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Items per page",
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse[T](BaseSchema):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


def paginate[T](
    items: list[T],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse[T]:
    pages = math.ceil(total / page_size) if page_size > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
