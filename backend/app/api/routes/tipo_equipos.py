"""TipoEquipos API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.tipo_equipos import (
    CreateTipoEquiposRequest,
    UpdateTipoEquiposRequest,
    TipoEquiposResponse,
    TipoEquiposListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.tipo_equipos import TipoEquipos
from backend.app.domain.models.user import User

router = APIRouter(prefix="/tipo-equipos", tags=["tipo-equipos"])


@router.get("", response_model=TipoEquiposListResponse)
async def list_tipo_equipos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> TipoEquiposListResponse:
    """List all TipoEquipos with pagination."""
    result = await db.execute(
        select(TipoEquipos).offset(skip).limit(limit)
    )
    items = result.scalars().all()

    total_result = await db.execute(select(func.count(TipoEquipos.id_tipo_equipos)))
    total = total_result.scalar() or 0

    return TipoEquiposListResponse(
        items=[TipoEquiposResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{tipo_id}", response_model=TipoEquiposResponse)
async def get_tipo_equipos(
    tipo_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> TipoEquiposResponse:
    """Get a TipoEquipos by ID."""
    result = await db.execute(
        select(TipoEquipos).where(TipoEquipos.id_tipo_equipos == tipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TipoEquipos not found")
    return TipoEquiposResponse.model_validate(item)


@router.post("", response_model=TipoEquiposResponse, status_code=status.HTTP_201_CREATED)
async def create_tipo_equipos(
    request: CreateTipoEquiposRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> TipoEquiposResponse:
    """Create a new TipoEquipos (admin only)."""
    item = TipoEquipos(nombre=request.nombre)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return TipoEquiposResponse.model_validate(item)


@router.put("/{tipo_id}", response_model=TipoEquiposResponse)
async def update_tipo_equipos(
    tipo_id: int,
    request: UpdateTipoEquiposRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> TipoEquiposResponse:
    """Update a TipoEquipos (admin only)."""
    result = await db.execute(
        select(TipoEquipos).where(TipoEquipos.id_tipo_equipos == tipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TipoEquipos not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return TipoEquiposResponse.model_validate(item)


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tipo_equipos(
    tipo_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a TipoEquipos (admin only)."""
    result = await db.execute(
        select(TipoEquipos).where(TipoEquipos.id_tipo_equipos == tipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TipoEquipos not found")

    await db.delete(item)
    return None
