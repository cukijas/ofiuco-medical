"""Client repository port."""

from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from backend.app.domain.models.client import Client


class IClientRepo(ABC):
    """Abstract client repository interface."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client."""
        ...

    @abstractmethod
    async def get_by_id(self, client_id: uuid.UUID) -> Optional[Client]:
        """Get client by ID."""
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Client]:
        """Get client by name."""
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get all active clients with pagination."""
        ...

    @abstractmethod
    async def count_active(self) -> int:
        """Count total active clients."""
        ...

    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Update an existing client."""
        ...

    @abstractmethod
    async def delete(self, client_id: uuid.UUID) -> bool:
        """Soft delete a client."""
        ...
