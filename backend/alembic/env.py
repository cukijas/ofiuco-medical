"""Alembic environment configuration for async PostgreSQL."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

import sys
import os

# Add /app to Python path so 'backend.app.*' imports work in Docker container
sys.path.insert(0, '/app')

from backend.app.infrastructure.database.base import Base
from backend.app.domain.models import *  # noqa: F401, F403 - import all models for autogenerate

# Import all models to register them with Base.metadata
from backend.app.domain.models.tipo_equipos import TipoEquipos
from backend.app.domain.models.subtipo_equipos import SubtipoEquipos
from backend.app.domain.models.marcas import Marcas
from backend.app.domain.models.empleados import Empleados
from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.departamentos import Departamentos
from backend.app.domain.models.equipos import Equipos
from backend.app.domain.models.equipos_subtipos import EquiposSubtipos
from backend.app.domain.models.ordenes_servicio import OrdenesServicio
from backend.app.domain.models.user import User

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url from DATABASE_URL environment variable if set
import os
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
