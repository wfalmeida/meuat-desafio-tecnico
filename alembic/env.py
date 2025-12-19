import sys
import os

sys.path.append(os.path.abspath("."))

from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db.models import Base
from app.core.config import DATABASE_URL

config = context.config

# Garantia defensiva
if not isinstance(DATABASE_URL, str):
    raise RuntimeError("DATABASE_URL não está definida corretamente")

config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """Inclui apenas tabelas específicas nas migrations automáticas."""
    if type_ == "table":
        return name in ("fazendas", "seed_control")
    return True


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
