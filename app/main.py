import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from .routes import (
    router_auth,
    router_perfil,
    router_usuarios,
    router_checkins,
    router_contactos,
    router_relevos,
    router_sos,
)
from . import models
from . import schemas
from .database import engine


logger = logging.getLogger(__name__)


def _initialize_database() -> None:
    """Aplica migraciones y crea cualquier tabla faltante al iniciar."""
    alembic_ini = Path(__file__).resolve().parent.parent / "alembic.ini"
    config = Config(str(alembic_ini))
    command.upgrade(config, "head")
    models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    secret = os.getenv("JWT_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET debe tener al menos 32 bytes aleatorios")
    await asyncio.to_thread(_initialize_database)
    yield


app = FastAPI(
    title="API RedCuidadora",
    version="2.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(router_auth)
app.include_router(router_perfil)
app.include_router(router_usuarios)
app.include_router(router_checkins)
app.include_router(router_contactos)
app.include_router(router_relevos)
app.include_router(router_sos)


@app.exception_handler(Exception)
async def manejar_error_no_controlado(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    """Registra internamente y devuelve una respuesta 500 JSON sin filtrar secretos."""
    logger.error(
        "Error no controlado durante una solicitud",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Error interno del servidor",
            "detail": "Error interno del servidor",
        },
    )


@app.get("/health", response_model=schemas.HealthOut, status_code=200)
def health():
    return {"status": "ok"}


@app.get("/hello", response_class=PlainTextResponse, include_in_schema=False)
def hello():
    return "Hello World"