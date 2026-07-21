"""Seed script for test data (Clientes, Departamentos, SubtipoEquipos, Equipos, OrdenesServicio).

Usage:
    docker exec ofiuco-medical-backend python -c "import sys; sys.path.insert(0, '/app'); exec(open('/app/backend/scripts/seed_test_data.py').read())"
"""

import asyncio
import os
import sys

sys.path.insert(0, os.environ.get("APP_PATH", "/app"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/ofiuco_medical",
)


async def seed_clientes(session: AsyncSession) -> None:
    """Insert test clientes (jurídica and física)."""
    stmt = text("""
        INSERT INTO clientes (tipo_cliente, nombre, telefono, email, razon_social, cuit, obra_social, direccion, localidad, dni) VALUES
            ('juridica', 'Sanatorio San Lucas', '376 4 42-0908', 'contacto@sanlucas.com', 'Sanatorio San Lucas S.A.', '30-71234567-9', 'OSDE', 'San Martín 1234', 'Posadas', NULL),
            ('fisica', 'Carlos Méndez', '376 4 55-1234', 'carlos.mendez@gmail.com', NULL, NULL, NULL, NULL, NULL, '38123456')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  Clientes: {result.rowcount} rows inserted")


async def seed_departamentos(session: AsyncSession) -> None:
    """Insert departamentos for Sanatorio San Lucas (id_cliente=1)."""
    stmt = text("""
        INSERT INTO departamentos (id_cliente, nombre) VALUES
            (1, 'Radiología'),
            (1, 'Oncología'),
            (1, 'Mastología')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  Departamentos: {result.rowcount} rows inserted")


async def seed_subtipo_equipos(session: AsyncSession) -> None:
    """Insert subtipo_equipos for Mamógrafo (id_tipo_equipos=1)."""
    stmt = text("""
        INSERT INTO subtipo_equipos (id_tipo_equipos, nombre) VALUES
            (1, 'Digital'),
            (1, 'Convencional')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  SubtipoEquipos: {result.rowcount} rows inserted")


async def seed_equipos(session: AsyncSession) -> None:
    """Insert test equipos."""
    stmt = text("""
        INSERT INTO equipos (id_tipo_equipos, id_marca, id_cliente, modelo, numero_serie, descripcion, condicion, accesorios, qr_identifier) VALUES
            (1, 1, 1, 'Microdose Mammography', 'PH-2024-001', 'Mamógrafo de alta definición para sala 3', 'usado', 'Compresor, pedal, cable de poder', 'QR-EQ-001'),
            (4, 2, 2, 'DigiRad 2000', 'TS-2023-045', 'Equipo de rayos X portátil', 'nuevo', NULL, 'QR-EQ-002')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  Equipos: {result.rowcount} rows inserted")


async def seed_equipos_subtipos(session: AsyncSession) -> None:
    """Link equipos to subtipo_equipos."""
    stmt = text("""
        INSERT INTO equipos_subtipos (id_equipos, id_subtipo) VALUES
            (1, 1)
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  EquiposSubtipos: {result.rowcount} rows inserted")


async def seed_ordenes_servicio(session: AsyncSession) -> None:
    """Insert test orden de servicio."""
    stmt = text("""
        INSERT INTO ordenes_servicio (numero_orden, numero_referencia, id_cliente, id_equipo, id_empleado, id_departamento, solicitado_por, tipo_visita, condicion_equipo, accesorios, fecha_realizacion, fecha_finalizacion, tarea_realizada, horas_trabajo, qr_identifier) VALUES
            ('000803', 'OS000803D', 1, 1, 1, 1, 'Dr. Roberto García', 'normal', 'usado', 'Compresor, pedal', '2026-07-19', '2026-07-20', 'Cambio de tubo de rayos X y calibración del sistema de imagen', 4.5, 'QR-OS-001')
        ON CONFLICT DO NOTHING
    """)
    result = await session.execute(stmt)
    print(f"  OrdenesServicio: {result.rowcount} rows inserted")


async def main() -> None:
    """Run all seed functions."""
    print("Seeding test data...")

    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            await seed_clientes(session)
            await seed_departamentos(session)
            await seed_subtipo_equipos(session)
            await seed_equipos(session)
            await seed_equipos_subtipos(session)
            await seed_ordenes_servicio(session)

        print("Done.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
