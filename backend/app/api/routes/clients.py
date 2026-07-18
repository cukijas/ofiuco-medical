"""Client API routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.client import (
    CreateClientRequest,
    UpdateClientRequest,
    ClientResponse,
    ClientListResponse,
)
from backend.app.application.services.client_service import ClientService
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.database.client_repo_impl import ClientRepo
from backend.app.infrastructure.database.service_order_repo_impl import ServiceOrderRepo
from backend.app.domain.models.user import User

import uuid

router = APIRouter(prefix="/clients", tags=["clients"])


def _build_service(db: AsyncSession) -> ClientService:
    """Create ClientService with its repository dependencies."""
    client_repo = ClientRepo(db)
    service_order_repo = ServiceOrderRepo(db)
    return ClientService(client_repo, service_order_repo)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
    request: CreateClientRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientResponse:
    """Create a new client.

    Args:
        request: Client creation data.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Created client data.
    """
    service = _build_service(db)
    return await service.create(request)


@router.get("", response_model=ClientListResponse)
async def list_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientListResponse:
    """List clients with pagination.

    Args:
        skip: Offset for pagination.
        limit: Maximum items per page.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Paginated list of clients.
    """
    service = _build_service(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientResponse:
    """Get a client by ID.

    Args:
        client_id: UUID of the client.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Client data.
    """
    service = _build_service(db)
    return await service.get_by_id(client_id)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    request: UpdateClientRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientResponse:
    """Update a client (partial update).

    Args:
        client_id: UUID of the client to update.
        request: Fields to update.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Updated client data.
    """
    service = _build_service(db)
    return await service.update(client_id, request)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a client (admin only).

    Args:
        client_id: UUID of the client to delete.
        current_user: Authenticated admin.
        db: Database session.
    """
    service = _build_service(db)
    await service.delete(client_id)
    return None
