"""Async session dependency for FastAPI."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.infrastructure.database.engine import create_engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session.

    This dependency is used in FastAPI route handlers.
    Reads DATABASE_URL from the environment.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    session = create_engine(database_url)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
