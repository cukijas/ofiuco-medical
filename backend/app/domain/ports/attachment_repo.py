"""Attachment repository port."""

from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from backend.app.domain.models.attachment import Attachment


class IAttachmentRepo(ABC):
    """Abstract attachment repository interface."""

    @abstractmethod
    async def create(self, attachment: Attachment) -> Attachment:
        """Create a new attachment."""
        ...

    @abstractmethod
    async def get_by_id(self, attachment_id: uuid.UUID) -> Optional[Attachment]:
        """Get attachment by ID."""
        ...

    @abstractmethod
    async def get_by_equipment(self, equipment_id: uuid.UUID) -> List[Attachment]:
        """Get attachments by equipment ID."""
        ...

    @abstractmethod
    async def get_by_order(self, order_id: uuid.UUID) -> List[Attachment]:
        """Get attachments by service order ID."""
        ...

    @abstractmethod
    async def delete(self, attachment_id: uuid.UUID) -> bool:
        """Soft-delete an attachment."""
        ...

    @abstractmethod
    async def update(self, attachment: Attachment) -> Attachment:
        """Update an existing attachment."""
        ...
