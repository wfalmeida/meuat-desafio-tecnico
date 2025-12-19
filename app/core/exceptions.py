import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("exceptions")


# -------------------- Handler HTTP --------------------
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Trata exceções HTTP e gera logs estruturados.
    """
    logger.warning(
        "HTTP exception",
        exc_info=exc,
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "method": request.method,
                "path": str(request.url),
            }
        },
    )


# -------------------- Handler SQLAlchemy --------------------
async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Trata erros de banco de dados e gera logs estruturados.
    """
    logger.error(
        "Database error",
        exc_info=exc,
        extra={
            "method": request.method,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "type": "database_error",
                "message": "Erro interno no banco de dados",
                "method": request.method,
                "path": str(request.url),
            }
        },
    )
