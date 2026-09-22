from fastapi import FastAPI

from .database import Base, engine
from .routes import router_usuarios, router_solicitudes

# Crea las tablas si no existen (a partir de los modelos)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Bienestar Estudiantil", version="1.0.0")

app.include_router(router_usuarios)
app.include_router(router_solicitudes)


@app.get("/health", status_code=200)
def health():
    """Endpoint simple para comprobar que la API está viva."""
    return {"status": "ok"}