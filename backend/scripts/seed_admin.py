"""Seed script to create the first admin user.

Usage:
    docker-compose exec backend python -m backend.scripts.seed_admin
"""

import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.domain.models.user import User
from backend.app.infrastructure.auth.password import hash_password


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/ofiuco_medical"


async def seed_admin():
    """Create the first admin user if none exists."""
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == "admin@ofiuco.com")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Admin user already exists: {existing.email}")
            return

        # Create admin user
        admin = User(
            email="admin@ofiuco.com",
            password_hash=hash_password("admin123"),
            full_name="Administrador",
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"✅ Admin user created: admin@ofiuco.com / admin123")
        print(f"   You can now login at http://localhost:8000/docs")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_admin())
