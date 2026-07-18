"""User repository implementation."""

from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.user import User
from backend.app.domain.ports.user_repo import IUserRepo


class UserRepo(IUserRepo):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update an existing user."""
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete a user."""
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            return True
        return False
