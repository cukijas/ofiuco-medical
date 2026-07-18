"""Service order application service."""

from datetime import date
from typing import Optional
import uuid

from fastapi import HTTPException, status as http_status

from backend.app.application.dtos.service_order import (
    CreateOrderRequest,
    UpdateOrderRequest,
    UpdateStatusRequest,
    OrderResponse,
    OrderListResponse,
    PartRequest,
    PartResponse,
)
from backend.app.domain.models.service_order import ServiceOrder
from backend.app.domain.models.service_order_part import ServiceOrderPart
from backend.app.domain.enums import StatusEnum
from backend.app.domain.ports.service_order_repo import IServiceOrderRepo
from backend.app.domain.ports.client_repo import IClientRepo
from backend.app.domain.ports.equipment_repo import IEquipmentRepo
from backend.app.domain.services.order_number import generate_order_number
from sqlalchemy.ext.asyncio import AsyncSession


# Allowed status transitions: current -> list of valid next statuses
VALID_TRANSITIONS: dict[StatusEnum, list[StatusEnum]] = {
    StatusEnum.draft: [StatusEnum.in_progress],
    StatusEnum.in_progress: [StatusEnum.completed],
    StatusEnum.completed: [StatusEnum.delivered],
    StatusEnum.delivered: [],
}


class OrderService:
    """Service layer for service order operations."""

    def __init__(
        self,
        service_order_repo: IServiceOrderRepo,
        client_repo: IClientRepo,
        equipment_repo: IEquipmentRepo,
        session: AsyncSession,
    ) -> None:
        self.repo = service_order_repo
        self.client_repo = client_repo
        self.equipment_repo = equipment_repo
        self.session = session

    async def create(
        self,
        request: CreateOrderRequest,
        current_user_id: uuid.UUID,
    ) -> OrderResponse:
        """Create a new service order.

        Auto-generates order number, validates client and equipment exist,
        sets status to draft.

        Args:
            request: Order creation data.
            current_user_id: UUID of the authenticated user (used as technician if not specified).

        Returns:
            Created order response with parts.

        Raises:
            HTTPException 404: If client or equipment not found.
        """
        # Validate client exists
        client = await self.client_repo.get_by_id(request.client_id)
        if not client or not client.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        # Validate equipment exists
        equipment = await self.equipment_repo.get_by_id(request.equipment_id)
        if not equipment or not equipment.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )

        # Auto-assign technician if not specified
        technician_id = request.technician_id or current_user_id

        # Generate order number
        order_number = await generate_order_number(self.session)

        order = ServiceOrder(
            order_number=order_number,
            client_id=request.client_id,
            equipment_id=request.equipment_id,
            technician_id=technician_id,
            status=StatusEnum.draft,
            description=request.description,
            service_date=request.service_date,
            requested_by=request.requested_by,
            department=request.department,
            visit_type=request.visit_type,
            equipment_condition=request.equipment_condition,
            declared_fault=request.declared_fault,
            accessories=request.accessories,
            work_hours=request.work_hours,
            operators_count=request.operators_count,
            kilometers=request.kilometers,
            travel_expenses=request.travel_expenses,
        )
        created = await self.repo.create(order)
        return await self._build_response(created)

    async def get_by_id(self, order_id: uuid.UUID) -> OrderResponse:
        """Get a service order by ID with its parts.

        Args:
            order_id: UUID of the order.

        Returns:
            Order response including parts.

        Raises:
            HTTPException 404: If order not found or inactive.
        """
        order = await self.repo.get_by_id(order_id)
        if not order or not order.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Service order not found",
            )
        return await self._build_response(order)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        client_id: Optional[uuid.UUID] = None,
        equipment_id: Optional[uuid.UUID] = None,
        order_status: Optional[StatusEnum] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> OrderListResponse:
        """List active service orders with optional filters and pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            client_id: Optional filter by client UUID.
            equipment_id: Optional filter by equipment UUID.
            order_status: Optional filter by status.
            date_from: Optional filter by minimum service date.
            date_to: Optional filter by maximum service date.

        Returns:
            Paginated order list.
        """
        items = await self.repo.get_filtered(
            skip=skip,
            limit=limit,
            client_id=client_id,
            equipment_id=equipment_id,
            status=order_status,
            date_from=date_from,
            date_to=date_to,
        )
        total = await self.repo.count_filtered(
            client_id=client_id,
            equipment_id=equipment_id,
            status=order_status,
            date_from=date_from,
            date_to=date_to,
        )
        responses = [await self._build_response(o) for o in items]
        return OrderListResponse(
            items=responses,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update(
        self,
        order_id: uuid.UUID,
        request: UpdateOrderRequest,
    ) -> OrderResponse:
        """Update a service order (partial update).

        Only allows updates while order is in draft or in_progress status.

        Args:
            order_id: UUID of the order to update.
            request: Fields to update.

        Returns:
            Updated order response.

        Raises:
            HTTPException 404: If order not found.
            HTTPException 409: If order is already completed or delivered.
            HTTPException 404: If referenced client or equipment not found.
        """
        order = await self.repo.get_by_id(order_id)
        if not order or not order.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Service order not found",
            )

        # Cannot modify completed or delivered orders
        if order.status in (StatusEnum.completed, StatusEnum.delivered):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Cannot modify order in '{order.status}' status",
            )

        update_data = request.model_dump(exclude_unset=True)

        # Validate client if changing
        if "client_id" in update_data:
            client = await self.client_repo.get_by_id(update_data["client_id"])
            if not client or not client.is_active:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Client not found",
                )

        # Validate equipment if changing
        if "equipment_id" in update_data:
            equipment = await self.equipment_repo.get_by_id(update_data["equipment_id"])
            if not equipment or not equipment.is_active:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Equipment not found",
                )

        for field, value in update_data.items():
            setattr(order, field, value)

        updated = await self.repo.update(order)
        return await self._build_response(updated)

    async def delete(self, order_id: uuid.UUID) -> None:
        """Soft-delete a service order.

        Args:
            order_id: UUID of the order to delete.

        Raises:
            HTTPException 404: If order not found.
        """
        order = await self.repo.get_by_id(order_id)
        if not order or not order.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Service order not found",
            )

        await self.repo.delete(order_id)

    async def update_status(
        self,
        order_id: uuid.UUID,
        request: UpdateStatusRequest,
    ) -> OrderResponse:
        """Transition the status of a service order with validation.

        Valid transitions:
            draft → in_progress → completed → delivered

        Args:
            order_id: UUID of the order.
            request: New status.

        Returns:
            Updated order response.

        Raises:
            HTTPException 404: If order not found.
            HTTPException 400: If status string is invalid.
            HTTPException 409: If transition is not allowed from current status.
        """
        order = await self.repo.get_by_id(order_id)
        if not order or not order.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Service order not found",
            )

        # Parse new status
        try:
            new_status = StatusEnum(request.status)
        except ValueError:
            valid_values = [s.value for s in StatusEnum]
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{request.status}'. Valid values: {valid_values}",
            )

        # Validate transition
        allowed_next = VALID_TRANSITIONS.get(order.status, [])
        if new_status not in allowed_next:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=(
                    f"Cannot transition from '{order.status}' to '{new_status}'. "
                    f"Valid transitions from '{order.status}': "
                    f"{[s.value for s in allowed_next] or ['(none — terminal state)']}"
                ),
            )

        order.status = new_status
        updated = await self.repo.update(order)
        return await self._build_response(updated)

    async def add_part(
        self,
        order_id: uuid.UUID,
        request: PartRequest,
    ) -> PartResponse:
        """Add a spare part to a service order.

        Only allowed while order is in draft or in_progress status.

        Args:
            order_id: UUID of the order.
            request: Part data.

        Returns:
            Created part response.

        Raises:
            HTTPException 404: If order not found.
            HTTPException 409: If order is completed or delivered.
        """
        order = await self.repo.get_by_id(order_id)
        if not order or not order.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Service order not found",
            )

        if order.status in (StatusEnum.completed, StatusEnum.delivered):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Cannot add parts to order in '{order.status}' status",
            )

        part = ServiceOrderPart(
            service_order_id=order_id,
            part_name=request.part_name,
            part_number=request.part_number,
            quantity=request.quantity,
            unit_cost=request.unit_cost,
        )
        created = await self.repo.add_part(part)
        return PartResponse.model_validate(created)

    async def remove_part(
        self,
        order_id: uuid.UUID,
        part_id: uuid.UUID,
    ) -> None:
        """Remove a part from a service order.

        Only allowed while order is in draft or in_progress status.

        Args:
            order_id: UUID of the order.
            part_id: UUID of the part to remove.

        Raises:
            HTTPException 404: If order or part not found.
            HTTPException 409: If order is completed or delivered.
        """
        order = await self.repo.get_by_id(order_id)
        if not order or not order.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Service order not found",
            )

        if order.status in (StatusEnum.completed, StatusEnum.delivered):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Cannot remove parts from order in '{order.status}' status",
            )

        part = await self.repo.get_part_by_id(part_id)
        if not part or not part.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Part not found",
            )

        if part.service_order_id != order_id:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Part does not belong to this order",
            )

        await self.repo.delete_part(part_id)

    async def _build_response(self, order: ServiceOrder) -> OrderResponse:
        """Build an OrderResponse including parts.

        Args:
            order: The service order domain model.

        Returns:
            Order response with embedded parts.
        """
        parts = await self.repo.get_parts_by_order_id(order.id)
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            client_id=order.client_id,
            equipment_id=order.equipment_id,
            technician_id=order.technician_id,
            status=order.status,
            description=order.description,
            diagnosis=order.diagnosis,
            solution=order.solution,
            service_date=order.service_date,
            next_service_date=order.next_service_date,
            requested_by=order.requested_by,
            department=order.department,
            visit_type=order.visit_type,
            equipment_condition=order.equipment_condition,
            declared_fault=order.declared_fault,
            accessories=order.accessories,
            work_hours=order.work_hours,
            operators_count=order.operators_count,
            kilometers=order.kilometers,
            travel_expenses=order.travel_expenses,
            is_active=order.is_active,
            created_at=order.created_at,
            updated_at=order.updated_at,
            parts=[PartResponse.model_validate(p) for p in parts],
        )
