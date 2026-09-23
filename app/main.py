from fastapi import FastAPI

from .database import Base, engine
from .routes import (
    router_usuarios,
    router_checkins,
    router_contactos,
    router_relevos,
    router_sos,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API RedCuidadora",
    version="2.0.0",
)

app.include_router(router_usuarios)
app.include_router(router_checkins)
app.include_router(router_contactos)
app.include_router(router_relevos)
app.include_router(router_sos)


@app.get("/health", status_code=200)
def health():
    return {"status": "ok"}