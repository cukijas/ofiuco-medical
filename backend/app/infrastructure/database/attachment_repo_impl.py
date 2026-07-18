"""Attachment repository implementation."""

from typing import List, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.attachment import Attachment
from backend.app.domain.ports.attachment_repo import IAttachmentRepo


class AttachmentRepo(IAttachmentRepo):
    """SQLAlchemy implementation of attachment repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, attachment: Attachment) -> Attachment:
        """Create a new attachment."""
        self.session.add(attachment)
        await self.session.flush()
        await self.session.refresh(attachment)
        return attachment

    async def get_by_id(self, attachment_id: uuid.UUID) -> Optional[Attachment]:
        """Get attachment by ID."""
        result = await self.session.execute(select(Attachment).where(Attachment.id == attachment_id))
        return result.scalar_one_or_none()

    async def get_by_equipment(self, equipment_id: uuid.UUID) -> List[Attachment]:
        """Get attachments by equipment ID."""
        result = await self.session.execute(
            select(Attachment).where(Attachment.equipment_id == equipment_id)
        )
        return list(result.scalars().all())

    async def get_by_order(self, order_id: uuid.UUID) -> List[Attachment]:
        """Get attachments by service order ID."""
        result = await self.session.execute(
            select(Attachment).where(Attachment.service_order_id == order_id)
        )
        return list(result.scalars().all())

    async def delete(self, attachment_id: uuid.UUID) -> bool:
        """Soft-delete an attachment."""
        attachment = await self.get_by_id(attachment_id)
        if attachment:
            attachment.is_active = False
            await self.session.flush()
            return True
        return False

    async def update(self, attachment: Attachment) -> Attachment:
        """Update an existing attachment."""
        await self.session.flush()
        await self.session.refresh(attachment)
        return attachment
