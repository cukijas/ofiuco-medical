"""SubtipoEquipos API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.subtipo_equipos import (
    CreateSubtipoEquiposRequest,
    UpdateSubtipoEquiposRequest,
    SubtipoEquiposResponse,
    SubtipoEquiposListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.subtipo_equipos import SubtipoEquipos
from backend.app.domain.models.tipo_equipos import TipoEquipos
from backend.app.domain.models.user import User

router = APIRouter(prefix="/subtipo-equipos", tags=["subtipo-equipos"])


@router.get("", response_model=SubtipoEquiposListResponse)
async def list_subtipo_equipos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    tipo_id: int | None = Query(None, description="Filter by tipo_equipos ID"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> SubtipoEquiposListResponse:
    """List all SubtipoEquipos with optional filter and pagination."""
    query = select(SubtipoEquipos)
    count_query = select(func.count(SubtipoEquipos.id_subtipo))

    if tipo_id is not None:
        query = query.where(SubtipoEquipos.id_tipo_equipos == tipo_id)
        count_query = count_query.where(SubtipoEquipos.id_tipo_equipos == tipo_id)

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return SubtipoEquiposListResponse(
        items=[SubtipoEquiposResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{subtipo_id}", response_model=SubtipoEquiposResponse)
async def get_subtipo_equipos(
    subtipo_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> SubtipoEquiposResponse:
    """Get a SubtipoEquipos by ID."""
    result = await db.execute(
        select(SubtipoEquipos).where(SubtipoEquipos.id_subtipo == subtipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SubtipoEquipos not found")
    return SubtipoEquiposResponse.model_validate(item)


@router.post("", response_model=SubtipoEquiposResponse, status_code=status.HTTP_201_CREATED)
async def create_subtipo_equipos(
    request: CreateSubtipoEquiposRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> SubtipoEquiposResponse:
    """Create a new SubtipoEquipos (admin only)."""
    parent = await db.execute(
        select(TipoEquipos).where(TipoEquipos.id_tipo_equipos == request.id_tipo_equipos)
    )
    if not parent.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent TipoEquipos not found")

    item = SubtipoEquipos(
        id_tipo_equipos=request.id_tipo_equipos,
        nombre=request.nombre,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return SubtipoEquiposResponse.model_validate(item)


@router.put("/{subtipo_id}", response_model=SubtipoEquiposResponse)
async def update_subtipo_equipos(
    subtipo_id: int,
    request: UpdateSubtipoEquiposRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> SubtipoEquiposResponse:
    """Update a SubtipoEquipos (admin only)."""
    result = await db.execute(
        select(SubtipoEquipos).where(SubtipoEquipos.id_subtipo == subtipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SubtipoEquipos not found")

    update_data = request.model_dump(exclude_unset=True)

    if "id_tipo_equipos" in update_data:
        parent = await db.execute(
            select(TipoEquipos).where(TipoEquipos.id_tipo_equipos == update_data["id_tipo_equipos"])
        )
        if not parent.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent TipoEquipos not found")

    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return SubtipoEquiposResponse.model_validate(item)


@router.delete("/{subtipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtipo_equipos(
    subtipo_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a SubtipoEquipos (admin only)."""
    result = await db.execute(
        select(SubtipoEquipos).where(SubtipoEquipos.id_subtipo == subtipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SubtipoEquipos not found")

    await db.delete(item)
    return None
