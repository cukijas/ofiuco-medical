"""Service order repository port."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
import uuid

from backend.app.domain.models.service_order import ServiceOrder
from backend.app.domain.models.service_order_part import ServiceOrderPart
from backend.app.domain.enums import StatusEnum


class IServiceOrderRepo(ABC):
    """Abstract service order repository interface."""

    @abstractmethod
    async def create(self, order: ServiceOrder) -> ServiceOrder:
        """Create a new service order."""
        ...

    @abstractmethod
    async def get_by_id(self, order_id: uuid.UUID) -> Optional[ServiceOrder]:
        """Get service order by ID."""
        ...

    @abstractmethod
    async def get_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: Optional[uuid.UUID] = None,
        equipment_id: Optional[uuid.UUID] = None,
        status: Optional[StatusEnum] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[ServiceOrder]:
        """Get active service orders with optional filters and pagination."""
        ...

    @abstractmethod
    async def count_filtered(
        self,
        client_id: Optional[uuid.UUID] = None,
        equipment_id: Optional[uuid.UUID] = None,
        status: Optional[StatusEnum] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        """Count active service orders matching optional filters."""
        ...

    @abstractmethod
    async def update(self, order: ServiceOrder) -> ServiceOrder:
        """Update an existing service order."""
        ...

    @abstractmethod
    async def delete(self, order_id: uuid.UUID) -> bool:
        """Soft delete a service order."""
        ...

    @abstractmethod
    async def get_max_order_number(self) -> Optional[str]:
        """Get the maximum order number for auto-numbering."""
        ...

    @abstractmethod
    async def has_active_by_client_id(self, client_id: uuid.UUID) -> bool:
        """Check if a client has any active service orders."""
        ...

    # --- Part methods ---

    @abstractmethod
    async def add_part(self, part: ServiceOrderPart) -> ServiceOrderPart:
        """Add a part to a service order."""
        ...

    @abstractmethod
    async def get_part_by_id(self, part_id: uuid.UUID) -> Optional[ServiceOrderPart]:
        """Get a part by ID."""
        ...

    @abstractmethod
    async def get_parts_by_order_id(self, order_id: uuid.UUID) -> List[ServiceOrderPart]:
        """Get all active parts for an order."""
        ...

    @abstractmethod
    async def delete_part(self, part_id: uuid.UUID) -> bool:
        """Soft delete a part."""
        ...
