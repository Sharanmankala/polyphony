from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import db_models
from app.database import Base, database_settings


config = context.config

# Alembic compares these ORM table definitions with the live database.
target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = database_settings.database_url.render_as_string(
    hide_password=False,
)

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
