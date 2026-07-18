"""Equipment repository implementation."""

from typing import List, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.equipment import Equipment
from backend.app.domain.ports.equipment_repo import IEquipmentRepo


class EquipmentRepo(IEquipmentRepo):
    """SQLAlchemy implementation of equipment repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, equipment: Equipment) -> Equipment:
        """Create a new equipment."""
        self.session.add(equipment)
        await self.session.flush()
        await self.session.refresh(equipment)
        return equipment

    async def get_by_id(self, equipment_id: uuid.UUID) -> Optional[Equipment]:
        """Get equipment by ID."""
        result = await self.session.execute(select(Equipment).where(Equipment.id == equipment_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Equipment]:
        """Get all active equipment with pagination."""
        result = await self.session.execute(
            select(Equipment)
            .where(Equipment.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
    ) -> List[Equipment]:
        """Get active equipment with optional filters."""
        query = select(Equipment).where(Equipment.is_active == True)

        if client_id is not None:
            query = query.where(Equipment.client_id == client_id)
        if category_id is not None:
            query = query.where(Equipment.category_id == category_id)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        client_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Count active equipment matching optional filters."""
        query = select(func.count(Equipment.id)).where(Equipment.is_active == True)

        if client_id is not None:
            query = query.where(Equipment.client_id == client_id)
        if category_id is not None:
            query = query.where(Equipment.category_id == category_id)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_by_qr(self, qr_code: str) -> Optional[Equipment]:
        """Get equipment by QR code."""
        result = await self.session.execute(select(Equipment).where(Equipment.qr_code == qr_code))
        return result.scalar_one_or_none()

    async def get_by_serial_number(self, serial_number: str) -> Optional[Equipment]:
        """Get equipment by serial number."""
        result = await self.session.execute(
            select(Equipment).where(Equipment.serial_number == serial_number)
        )
        return result.scalar_one_or_none()

    async def update(self, equipment: Equipment) -> Equipment:
        """Update an existing equipment."""
        await self.session.flush()
        await self.session.refresh(equipment)
        return equipment

    async def delete(self, equipment_id: uuid.UUID) -> bool:
        """Soft delete equipment."""
        equipment = await self.get_by_id(equipment_id)
        if equipment:
            equipment.is_active = False
            await self.session.flush()
            return True
        return False
