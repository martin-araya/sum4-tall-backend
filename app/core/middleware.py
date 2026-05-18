import time
import uuid
from typing import Any
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger("auditchain.middleware")


class AuditChainMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # 1. Correlation ID / Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Clear and bind contextvars for structlog (correlation ID propagation)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Store in request state
        request.state.request_id = request_id

        # 2. Request Timing
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            # Record response headers
            response.headers["X-Request-ID"] = request_id

            # Calculate and record process time
            process_time = time.perf_counter() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"

            logger.info(
                "http.request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=f"{process_time:.4f}s",
            )
            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                "http.request.failed",
                method=request.method,
                path=request.url.path,
                duration=f"{process_time:.4f}s",
                error=str(e),
            )
            raise
