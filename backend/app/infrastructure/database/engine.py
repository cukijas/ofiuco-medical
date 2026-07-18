"""Async SQLAlchemy engine creation."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.infrastructure.database.base import Base
from backend.app.domain.models import *  # noqa: F401, F403 - import all models to register them


def create_engine(database_url: str) -> AsyncSession:
    """Create async engine and session factory.

    Args:
        database_url: PostgreSQL async connection URL.

    Returns:
        AsyncSession instance.
    """
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session_factory()


async def init_db() -> None:
    """Initialize database tables (for development)."""
    from sqlalchemy import text
    from backend.app.infrastructure.database.engine import create_engine
    # This is a placeholder; in production we use Alembic migrations.
    pass
