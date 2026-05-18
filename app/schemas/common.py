from typing import Generic, TypeVar

from app.schemas.base import BaseSchema
from app.schemas.pagination import Page

T = TypeVar("T")

# PaginatedResponse is equivalent to Page, inherits from BaseSchema
PaginatedResponse = Page
