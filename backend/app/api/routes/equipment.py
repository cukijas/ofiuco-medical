"""Equipment API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.equipment import (
    CreateEquipmentRequest,
    UpdateEquipmentRequest,
    EquipmentResponse,
    EquipmentListResponse,
)
from backend.app.application.services.equipment_service import EquipmentService
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import get_current_user, require_role
from backend.app.infrastructure.database.equipment_repo_impl import EquipmentRepo
from backend.app.infrastructure.database.client_repo_impl import ClientRepo
from backend.app.infrastructure.database.category_repo_impl import CategoryRepo
from backend.app.infrastructure.qr.generator import generate_qr_png
from backend.app.domain.models.user import User

import uuid

router = APIRouter(prefix="/equipment", tags=["equipment"])


def _build_service(db: AsyncSession) -> EquipmentService:
    """Create EquipmentService with its repository dependencies."""
    equipment_repo = EquipmentRepo(db)
    client_repo = ClientRepo(db)
    category_repo = CategoryRepo(db)
    return EquipmentService(equipment_repo, client_repo, category_repo)


@router.post(
    "",
    response_model=EquipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment(
    request: CreateEquipmentRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    """Create new equipment with auto-generated QR code.

    Args:
        request: Equipment creation data.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Created equipment data including the generated QR code token.
    """
    service = _build_service(db)
    return await service.create(request)


@router.get("", response_model=EquipmentListResponse)
async def list_equipment(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client UUID"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category UUID"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquipmentListResponse:
    """List equipment with optional filters and pagination.

    Args:
        skip: Offset for pagination.
        limit: Maximum items per page.
        client_id: Optional client filter.
        category_id: Optional category filter.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Paginated list of equipment.
    """
    service = _build_service(db)
    return await service.get_all(skip=skip, limit=limit, client_id=client_id, category_id=category_id)


@router.get("/qr/{qr_code}", response_model=EquipmentResponse)
async def get_equipment_by_qr(
    qr_code: str,
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    """Get equipment by QR code (public — no auth required).

    Args:
        qr_code: QR code token string.
        db: Database session.

    Returns:
        Equipment data for the given QR code.
    """
    service = _build_service(db)
    return await service.get_by_qr(qr_code)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    """Get equipment by ID.

    Args:
        equipment_id: UUID of the equipment.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Equipment data.
    """
    service = _build_service(db)
    return await service.get_by_id(equipment_id)


@router.get("/{equipment_id}/qr-image")
async def get_qr_image(
    equipment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download QR code image for equipment as PNG.

    The QR code encodes a URL pointing to the public equipment lookup endpoint.

    Args:
        equipment_id: UUID of the equipment.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        PNG image response with appropriate content type.
    """
    service = _build_service(db)
    equipment = await service.get_by_id(equipment_id)

    # Build the URL the QR code should encode
    qr_url = f"/api/v1/equipment/qr/{equipment.qr_code}"
    qr_png = generate_qr_png(qr_url)

    return Response(content=qr_png, media_type="image/png")


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: uuid.UUID,
    request: UpdateEquipmentRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    """Update equipment (partial update).

    Args:
        equipment_id: UUID of the equipment to update.
        request: Fields to update.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Updated equipment data.
    """
    service = _build_service(db)
    return await service.update(equipment_id, request)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete equipment (admin only).

    Args:
        equipment_id: UUID of the equipment to delete.
        current_user: Authenticated admin.
        db: Database session.
    """
    service = _build_service(db)
    await service.delete(equipment_id)
    return None
