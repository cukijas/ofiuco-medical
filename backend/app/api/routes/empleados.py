"""Empleados API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.empleados import (
    CreateEmpleadosRequest,
    UpdateEmpleadosRequest,
    EmpleadosResponse,
    EmpleadosListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.empleados import Empleados
from backend.app.domain.models.user import User

router = APIRouter(prefix="/empleados", tags=["empleados"])


@router.get("", response_model=EmpleadosListResponse)
async def list_empleados(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    activo: bool | None = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EmpleadosListResponse:
    """List all Empleados with optional filter and pagination."""
    query = select(Empleados)
    count_query = select(func.count(Empleados.id_empleado))

    if activo is not None:
        query = query.where(Empleados.activo == activo)
        count_query = count_query.where(Empleados.activo == activo)

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return EmpleadosListResponse(
        items=[EmpleadosResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{empleado_id}", response_model=EmpleadosResponse)
async def get_empleados(
    empleado_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EmpleadosResponse:
    """Get an Empleados by ID."""
    result = await db.execute(
        select(Empleados).where(Empleados.id_empleado == empleado_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleados not found")
    return EmpleadosResponse.model_validate(item)


@router.post("", response_model=EmpleadosResponse, status_code=status.HTTP_201_CREATED)
async def create_empleados(
    request: CreateEmpleadosRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> EmpleadosResponse:
    """Create a new Empleados (admin only)."""
    item = Empleados(
        nombre=request.nombre,
        especialidad=request.especialidad,
        telefono=request.telefono,
        email=request.email,
        activo=request.activo,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return EmpleadosResponse.model_validate(item)


@router.put("/{empleado_id}", response_model=EmpleadosResponse)
async def update_empleados(
    empleado_id: int,
    request: UpdateEmpleadosRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> EmpleadosResponse:
    """Update an Empleados (admin only)."""
    result = await db.execute(
        select(Empleados).where(Empleados.id_empleado == empleado_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleados not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return EmpleadosResponse.model_validate(item)


@router.delete("/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_empleados(
    empleado_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an Empleados (admin only)."""
    result = await db.execute(
        select(Empleados).where(Empleados.id_empleado == empleado_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleados not found")

    await db.delete(item)
    return None
