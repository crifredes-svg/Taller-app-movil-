from logging.config import fileConfig

from alembic import context

from app import models
from app.database import DATABASE_URL, engine


# Alembic Config, que permite acceder a los valores de alembic.ini.
config = context.config

# Alembic utilizará la misma URL de base de datos que la aplicación.
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.render_as_string(hide_password=True).replace("%", "%%"),
)

# Configura los registros definidos en alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Los modelos se importan arriba para registrarlos en Base.metadata.
target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta las migraciones sin crear una conexión directa."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta las migraciones utilizando una conexión a la base de datos."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()