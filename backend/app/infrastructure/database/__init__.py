"""Infrastructure database package."""

from backend.app.infrastructure.database.base import Base
from backend.app.infrastructure.database.session import get_db

__all__ = [
    "Base",
    "get_db",
]
