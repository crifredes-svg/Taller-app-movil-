import os

from sqlalchemy import URL, create_engine, make_url
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    database_url = make_url(DATABASE_URL)
    if database_url.get_backend_name() not in {"mysql", "mariadb"}:
        raise RuntimeError("La aplicación requiere MySQL o MariaDB en 1Panel.")
    DATABASE_URL = database_url.set(
        drivername="mysql+pymysql",
    ).render_as_string(hide_password=False)
else:
    db_host = os.getenv("DB_HOST")
    if not db_host:
        raise RuntimeError(
            "Configura DATABASE_URL o DB_HOST con los datos de MySQL/MariaDB "
            "del servidor. No se crea una base local."
        )

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    missing = [
        name
        for name, value in (
            ("DB_USER", db_user),
            ("DB_PASSWORD", db_password),
            ("DB_NAME", db_name),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Faltan variables de conexión a MySQL/MariaDB: "
            + ", ".join(missing)
        )

    DATABASE_URL = URL.create(
        "mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(os.getenv("DB_PORT", "3306")),
        database=db_name,
    ).render_as_string(hide_password=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    """Entrega una sesión de base de datos por cada petición y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()