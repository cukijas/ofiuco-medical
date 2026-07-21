"""User repository port."""

from abc import ABC, abstractmethod
from typing import Optional

from backend.app.domain.models.user import User


class IUserRepo(ABC):
    """Abstract user repository interface."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        ...
