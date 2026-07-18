"""Service order API routes."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.service_order import (
    CreateOrderRequest,
    UpdateOrderRequest,
    UpdateStatusRequest,
    OrderResponse,
    OrderListResponse,
    PartRequest,
    PartResponse,
)
from backend.app.application.services.order_service import OrderService
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.database.service_order_repo_impl import ServiceOrderRepo
from backend.app.infrastructure.database.client_repo_impl import ClientRepo
from backend.app.infrastructure.database.equipment_repo_impl import EquipmentRepo
from backend.app.domain.models.user import User

import uuid

router = APIRouter(prefix="/orders", tags=["service-orders"])


def _build_service(db: AsyncSession) -> OrderService:
    """Create OrderService with its repository dependencies."""
    service_order_repo = ServiceOrderRepo(db)
    client_repo = ClientRepo(db)
    equipment_repo = EquipmentRepo(db)
    return OrderService(service_order_repo, client_repo, equipment_repo, db)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Create a new service order.

    Auto-generates order number (OS-XXXXD) and sets status to draft.
    If technician_id is omitted, the current user is assigned.

    Args:
        request: Order creation data.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Created order data with empty parts list.
    """
    service = _build_service(db)
    return await service.create(request, current_user.id)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client UUID"),
    equipment_id: Optional[uuid.UUID] = Query(None, description="Filter by equipment UUID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    date_from: Optional[date] = Query(None, description="Filter by minimum service date"),
    date_to: Optional[date] = Query(None, description="Filter by maximum service date"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrderListResponse:
    """List service orders with optional filters and pagination.

    Args:
        skip: Offset for pagination.
        limit: Maximum items per page.
        client_id: Optional client filter.
        equipment_id: Optional equipment filter.
        status_filter: Optional status filter (draft, in_progress, completed, delivered).
        date_from: Optional minimum service date.
        date_to: Optional maximum service date.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Paginated list of service orders.
    """
    # Parse status filter
    from backend.app.domain.enums import StatusEnum

    parsed_status = None
    if status_filter:
        try:
            parsed_status = StatusEnum(status_filter)
        except ValueError:
            pass  # Invalid status returns empty list

    service = _build_service(db)
    return await service.get_all(
        skip=skip,
        limit=limit,
        client_id=client_id,
        equipment_id=equipment_id,
        order_status=parsed_status,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Get a service order by ID with its parts.

    Args:
        order_id: UUID of the order.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Order data including parts.
    """
    service = _build_service(db)
    return await service.get_by_id(order_id)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: uuid.UUID,
    request: UpdateOrderRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Update a service order (partial update).

    Only allowed while order is in draft or in_progress status.

    Args:
        order_id: UUID of the order to update.
        request: Fields to update.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Updated order data.
    """
    service = _build_service(db)
    return await service.update(order_id, request)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a service order (admin only).

    Args:
        order_id: UUID of the order to delete.
        current_user: Authenticated admin.
        db: Database session.
    """
    service = _build_service(db)
    await service.delete(order_id)
    return None


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: uuid.UUID,
    request: UpdateStatusRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Update service order status with transition validation.

    Valid transitions: draft → in_progress → completed → delivered

    Args:
        order_id: UUID of the order.
        request: New status.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Updated order data.
    """
    service = _build_service(db)
    return await service.update_status(order_id, request)


@router.post(
    "/{order_id}/parts",
    response_model=PartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_part(
    order_id: uuid.UUID,
    request: PartRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> PartResponse:
    """Add a spare part to a service order.

    Only allowed while order is in draft or in_progress status.

    Args:
        order_id: UUID of the order.
        request: Part data.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Created part data.
    """
    service = _build_service(db)
    return await service.add_part(order_id, request)


@router.delete(
    "/{order_id}/parts/{part_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_part(
    order_id: uuid.UUID,
    part_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a part from a service order.

    Only allowed while order is in draft or in_progress status.

    Args:
        order_id: UUID of the order.
        part_id: UUID of the part to remove.
        current_user: Authenticated admin or technician.
        db: Database session.
    """
    service = _build_service(db)
    await service.remove_part(order_id, part_id)
    return None
