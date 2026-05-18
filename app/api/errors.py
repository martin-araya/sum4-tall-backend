import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import DomainError

logger = logging.getLogger("auditchain.errors")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning(
            "Domain error occurred: %s (code=%s)",
            exc.message,
            exc.code,
            extra={"context": exc.ctx},
        )
        return JSONResponse(
            status_code=exc.status,
            content={
                "detail": exc.message,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "context": exc.ctx,
                }
            },
        )
