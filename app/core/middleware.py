import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging estruturado de requisições HTTP.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        logger.info(
            "request_started",
            extra={
                "method": request.method,
                "path": str(request.url),
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": str(request.url),
                },
            )
            raise exc

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "request_finished",
            extra={
                "method": request.method,
                "path": str(request.url),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
