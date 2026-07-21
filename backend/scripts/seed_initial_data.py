"""Seed script for initial TipoEquipos, Marcas, and Empleados data.

Usage:
    docker-compose exec backend python -m backend.scripts.seed_initial_data
"""

import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/ofiuco_medical",
)


async def seed_tipo_equipos(session: AsyncSession) -> None:
    """Insert initial TipoEquipos if they don't exist."""
    stmt = text("""
        INSERT INTO tipo_equipos (nombre) VALUES
            ('Mamografo'),
            ('Tomografos'),
            ('Arco en C'),
            ('Rayos X')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  TipoEquipos: {result.rowcount} rows inserted")


async def seed_marcas(session: AsyncSession) -> None:
    """Insert initial Marcas if they don't exist."""
    stmt = text("""
        INSERT INTO marcas (nombre) VALUES
            ('Philip'),
            ('Toshiba'),
            ('Rolco')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  Marcas: {result.rowcount} rows inserted")


async def seed_empleados(session: AsyncSession) -> None:
    """Insert initial Empleados if they don't exist."""
    stmt = text("""
        INSERT INTO empleados (nombre, especialidad, activo) VALUES
            ('Juan Romero', 'Tecnico Avanzado', true),
            ('Mateo Kruki', 'Tecnico Moderado', true),
            ('Ivan Romero', 'Tecnico Principiante', true)
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  Empleados: {result.rowcount} rows inserted")


async def main() -> None:
    """Run all seed functions."""
    print("Seeding initial data...")

    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            await seed_tipo_equipos(session)
            await seed_marcas(session)
            await seed_empleados(session)

        print("Done.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
