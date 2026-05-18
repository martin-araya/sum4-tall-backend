import math
from typing import Generic, TypeVar

from app.schemas.base import BaseSchema

T = TypeVar("T")


class Page(BaseSchema, Generic[T]):
    """Standard paginated response schema matching the AGENT_FASTAPI architecture."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, size: int) -> "Page[T]":
        pages = math.ceil(total / size) if size > 0 else 0
        return cls(items=items, total=total, page=page, size=size, pages=pages)
