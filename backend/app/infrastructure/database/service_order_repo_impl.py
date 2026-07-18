"""Service order repository implementation."""

from datetime import date
from typing import List, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.service_order import ServiceOrder
from backend.app.domain.models.service_order_part import ServiceOrderPart
from backend.app.domain.enums import StatusEnum
from backend.app.domain.ports.service_order_repo import IServiceOrderRepo


class ServiceOrderRepo(IServiceOrderRepo):
    """SQLAlchemy implementation of service order repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, order: ServiceOrder) -> ServiceOrder:
        """Create a new service order."""
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: uuid.UUID) -> Optional[ServiceOrder]:
        """Get service order by ID."""
        result = await self.session.execute(
            select(ServiceOrder).where(ServiceOrder.id == order_id)
        )
        return result.scalar_one_or_none()

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
        query = select(ServiceOrder).where(ServiceOrder.is_active == True)

        if client_id is not None:
            query = query.where(ServiceOrder.client_id == client_id)
        if equipment_id is not None:
            query = query.where(ServiceOrder.equipment_id == equipment_id)
        if status is not None:
            query = query.where(ServiceOrder.status == status)
        if date_from is not None:
            query = query.where(ServiceOrder.service_date >= date_from)
        if date_to is not None:
            query = query.where(ServiceOrder.service_date <= date_to)

        query = query.order_by(ServiceOrder.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        client_id: Optional[uuid.UUID] = None,
        equipment_id: Optional[uuid.UUID] = None,
        status: Optional[StatusEnum] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        """Count active service orders matching optional filters."""
        query = select(func.count(ServiceOrder.id)).where(ServiceOrder.is_active == True)

        if client_id is not None:
            query = query.where(ServiceOrder.client_id == client_id)
        if equipment_id is not None:
            query = query.where(ServiceOrder.equipment_id == equipment_id)
        if status is not None:
            query = query.where(ServiceOrder.status == status)
        if date_from is not None:
            query = query.where(ServiceOrder.service_date >= date_from)
        if date_to is not None:
            query = query.where(ServiceOrder.service_date <= date_to)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update(self, order: ServiceOrder) -> ServiceOrder:
        """Update an existing service order."""
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def delete(self, order_id: uuid.UUID) -> bool:
        """Soft delete a service order."""
        order = await self.get_by_id(order_id)
        if order:
            order.is_active = False
            await self.session.flush()
            return True
        return False

    async def get_max_order_number(self) -> Optional[str]:
        """Get the maximum order number for auto-numbering."""
        result = await self.session.execute(
            select(func.max(ServiceOrder.order_number))
        )
        return result.scalar_one_or_none()

    async def has_active_by_client_id(self, client_id: uuid.UUID) -> bool:
        """Check if a client has any active service orders."""
        result = await self.session.execute(
            select(func.count(ServiceOrder.id)).where(
                ServiceOrder.client_id == client_id,
                ServiceOrder.is_active == True,
            )
        )
        count = result.scalar()
        return (count or 0) > 0

    # --- Part methods ---

    async def add_part(self, part: ServiceOrderPart) -> ServiceOrderPart:
        """Add a part to a service order."""
        self.session.add(part)
        await self.session.flush()
        await self.session.refresh(part)
        return part

    async def get_part_by_id(self, part_id: uuid.UUID) -> Optional[ServiceOrderPart]:
        """Get a part by ID."""
        result = await self.session.execute(
            select(ServiceOrderPart).where(ServiceOrderPart.id == part_id)
        )
        return result.scalar_one_or_none()

    async def get_parts_by_order_id(self, order_id: uuid.UUID) -> List[ServiceOrderPart]:
        """Get all active parts for an order."""
        result = await self.session.execute(
            select(ServiceOrderPart).where(
                ServiceOrderPart.service_order_id == order_id,
                ServiceOrderPart.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def delete_part(self, part_id: uuid.UUID) -> bool:
        """Soft delete a part."""
        part = await self.get_part_by_id(part_id)
        if part:
            part.is_active = False
            await self.session.flush()
            return True
        return False
