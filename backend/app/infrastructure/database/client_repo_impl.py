"""Client repository implementation."""

from typing import List, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.client import Client
from backend.app.domain.ports.client_repo import IClientRepo


class ClientRepo(IClientRepo):
    """SQLAlchemy implementation of client repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, client: Client) -> Client:
        """Create a new client."""
        self.session.add(client)
        await self.session.flush()
        await self.session.refresh(client)
        return client

    async def get_by_id(self, client_id: uuid.UUID) -> Optional[Client]:
        """Get client by ID."""
        result = await self.session.execute(select(Client).where(Client.id == client_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Client]:
        """Get client by name."""
        result = await self.session.execute(select(Client).where(Client.name == name))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get all active clients with pagination."""
        result = await self.session.execute(
            select(Client)
            .where(Client.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Count total active clients."""
        result = await self.session.execute(
            select(func.count(Client.id)).where(Client.is_active == True)
        )
        return result.scalar() or 0

    async def update(self, client: Client) -> Client:
        """Update an existing client."""
        await self.session.flush()
        await self.session.refresh(client)
        return client

    async def delete(self, client_id: uuid.UUID) -> bool:
        """Soft delete a client."""
        client = await self.get_by_id(client_id)
        if client:
            client.is_active = False
            await self.session.flush()
            return True
        return False
