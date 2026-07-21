"""Clientes API routes for the new integer-PK Clientes table."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.clientes import (
    CreateClientesRequest,
    UpdateClientesRequest,
    ClientesResponse,
    ClientesListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.user import User

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=ClientesListResponse)
async def list_clientes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    tipo_cliente: str | None = Query(None, description="Filter by tipo_cliente"),
    search: str | None = Query(None, description="Search by nombre"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientesListResponse:
    """List all Clientes with optional filters and pagination."""
    query = select(Clientes)
    count_query = select(func.count(Clientes.id_cliente))

    if tipo_cliente is not None:
        query = query.where(Clientes.tipo_cliente == tipo_cliente)
        count_query = count_query.where(Clientes.tipo_cliente == tipo_cliente)
    if search is not None:
        query = query.where(Clientes.nombre.ilike(f"%{search}%"))
        count_query = count_query.where(Clientes.nombre.ilike(f"%{search}%"))

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return ClientesListResponse(
        items=[ClientesResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{cliente_id}", response_model=ClientesResponse)
async def get_clientes(
    cliente_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientesResponse:
    """Get a Clientes by ID."""
    result = await db.execute(
        select(Clientes).where(Clientes.id_cliente == cliente_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clientes not found")
    return ClientesResponse.model_validate(item)


@router.post("", response_model=ClientesResponse, status_code=status.HTTP_201_CREATED)
async def create_clientes(
    request: CreateClientesRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientesResponse:
    """Create a new Clientes."""
    item = Clientes(
        tipo_cliente=request.tipo_cliente,
        nombre=request.nombre,
        telefono=request.telefono,
        email=request.email,
        razon_social=request.razon_social,
        cuit=request.cuit,
        obra_social=request.obra_social,
        direccion=request.direccion,
        localidad=request.localidad,
        dni=request.dni,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return ClientesResponse.model_validate(item)


@router.put("/{cliente_id}", response_model=ClientesResponse)
async def update_clientes(
    cliente_id: int,
    request: UpdateClientesRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> ClientesResponse:
    """Update a Clientes (partial update)."""
    result = await db.execute(
        select(Clientes).where(Clientes.id_cliente == cliente_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clientes not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return ClientesResponse.model_validate(item)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clientes(
    cliente_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a Clientes (admin only)."""
    result = await db.execute(
        select(Clientes).where(Clientes.id_cliente == cliente_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clientes not found")

    await db.delete(item)
    return None
