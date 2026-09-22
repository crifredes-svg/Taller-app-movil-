import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# El motor de base de datos se lee de una variable de entorno.
# Por defecto usamos SQLite para pruebas locales.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    """Entrega una sesión de base de datos por cada petición y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()