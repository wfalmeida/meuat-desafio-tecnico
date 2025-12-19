from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware
from app.core.exceptions import http_exception_handler, sqlalchemy_exception_handler
from app.api import routes

# -------------------- Logger --------------------
logger = logging.getLogger("main")


# -------------------- Lifespan --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("startup", extra={"event": "app_start"})
    yield
    # Shutdown
    logger.info("shutdown", extra={"event": "app_stop"})


# -------------------- App --------------------
app = FastAPI(
    title="MeuAT – API Geoespacial",
    description="API para consulta de fazendas com PostGIS",
    version="1.0.0",
    lifespan=lifespan,
)


# -------------------- Middlewares --------------------
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Exception Handlers --------------------
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)


# -------------------- Routers --------------------
app.include_router(routes.router)


# -------------------- Health Check --------------------
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check DB",
    description="Verifica conectividade com o banco de dados",
    tags=["Health"],
)
def health_check(db: Session = Depends(routes.get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info(
            "health_check_ok",
            extra={"method": "GET", "path": "/health", "status_code": 200},
        )
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError as exc:
        logger.error("health_check_fail", extra={"method": "GET", "path": "/health"})
        raise HTTPException(
            status_code=503, detail="Banco de dados inacessível"
        ) from exc
