import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    db_host = os.getenv("DB_HOST")
    if not db_host:
        raise RuntimeError(
            "Configura DATABASE_URL o DB_HOST con los datos de la base "
            "de datos del servidor. No se crea una base local automáticamente."
        )

    DATABASE_URL = URL.create(
        "postgresql+psycopg",
        username=os.getenv("DB_USER", "postgres_user"),
        password=os.getenv("DB_PASSWORD", "postgres_password"),
        host=db_host,
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "redcuidadora_db"),
    ).render_as_string(hide_password=False)

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