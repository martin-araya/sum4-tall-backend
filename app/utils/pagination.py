from fastapi import Query


class PaginationParams:
    """FastAPI dependency class for standard query parameter pagination."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número de página (comienza en 1)"),
        size: int = Query(20, ge=1, le=100, description="Tamaño de la página (máximo 100)"),
    ) -> None:
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        """Offset calculated based on page and page size."""
        return (self.page - 1) * self.size
