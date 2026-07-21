"""Departamentos API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.departamentos import (
    CreateDepartamentosRequest,
    UpdateDepartamentosRequest,
    DepartamentosResponse,
    DepartamentosListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.departamentos import Departamentos
from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.user import User

router = APIRouter(prefix="/departamentos", tags=["departamentos"])


@router.get("", response_model=DepartamentosListResponse)
async def list_departamentos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    cliente_id: int | None = Query(None, description="Filter by cliente ID"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> DepartamentosListResponse:
    """List all Departamentos with optional filter and pagination."""
    query = select(Departamentos)
    count_query = select(func.count(Departamentos.id_departamento))

    if cliente_id is not None:
        query = query.where(Departamentos.id_cliente == cliente_id)
        count_query = count_query.where(Departamentos.id_cliente == cliente_id)

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return DepartamentosListResponse(
        items=[DepartamentosResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{departamento_id}", response_model=DepartamentosResponse)
async def get_departamentos(
    departamento_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> DepartamentosResponse:
    """Get a Departamentos by ID."""
    result = await db.execute(
        select(Departamentos).where(Departamentos.id_departamento == departamento_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departamentos not found")
    return DepartamentosResponse.model_validate(item)


@router.post("", response_model=DepartamentosResponse, status_code=status.HTTP_201_CREATED)
async def create_departamentos(
    request: CreateDepartamentosRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> DepartamentosResponse:
    """Create a new Departamentos (admin only)."""
    parent = await db.execute(
        select(Clientes).where(Clientes.id_cliente == request.id_cliente)
    )
    if not parent.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent Clientes not found")

    item = Departamentos(
        id_cliente=request.id_cliente,
        nombre=request.nombre,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return DepartamentosResponse.model_validate(item)


@router.put("/{departamento_id}", response_model=DepartamentosResponse)
async def update_departamentos(
    departamento_id: int,
    request: UpdateDepartamentosRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> DepartamentosResponse:
    """Update a Departamentos (admin only)."""
    result = await db.execute(
        select(Departamentos).where(Departamentos.id_departamento == departamento_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departamentos not found")

    update_data = request.model_dump(exclude_unset=True)

    if "id_cliente" in update_data:
        parent = await db.execute(
            select(Clientes).where(Clientes.id_cliente == update_data["id_cliente"])
        )
        if not parent.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent Clientes not found")

    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return DepartamentosResponse.model_validate(item)


@router.delete("/{departamento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_departamentos(
    departamento_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a Departamentos (admin only)."""
    result = await db.execute(
        select(Departamentos).where(Departamentos.id_departamento == departamento_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departamentos not found")

    await db.delete(item)
    return None
