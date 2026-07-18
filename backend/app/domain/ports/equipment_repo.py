"""Equipment repository port."""

from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from backend.app.domain.models.equipment import Equipment


class IEquipmentRepo(ABC):
    """Abstract equipment repository interface."""

    @abstractmethod
    async def create(self, equipment: Equipment) -> Equipment:
        """Create a new equipment."""
        ...

    @abstractmethod
    async def get_by_id(self, equipment_id: uuid.UUID) -> Optional[Equipment]:
        """Get equipment by ID."""
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Equipment]:
        """Get all active equipment with pagination."""
        ...

    @abstractmethod
    async def get_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
    ) -> List[Equipment]:
        """Get active equipment with optional filters."""
        ...

    @abstractmethod
    async def count_filtered(
        self,
        client_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Count active equipment matching optional filters."""
        ...

    @abstractmethod
    async def get_by_qr(self, qr_code: str) -> Optional[Equipment]:
        """Get equipment by QR code."""
        ...

    @abstractmethod
    async def get_by_serial_number(self, serial_number: str) -> Optional[Equipment]:
        """Get equipment by serial number."""
        ...

    @abstractmethod
    async def update(self, equipment: Equipment) -> Equipment:
        """Update an existing equipment."""
        ...

    @abstractmethod
    async def delete(self, equipment_id: uuid.UUID) -> bool:
        """Soft delete equipment."""
        ...
