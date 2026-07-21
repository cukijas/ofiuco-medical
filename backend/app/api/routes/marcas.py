"""Marcas API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.marcas import (
    CreateMarcasRequest,
    UpdateMarcasRequest,
    MarcasResponse,
    MarcasListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.marcas import Marcas
from backend.app.domain.models.user import User

router = APIRouter(prefix="/marcas", tags=["marcas"])


@router.get("", response_model=MarcasListResponse)
async def list_marcas(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> MarcasListResponse:
    """List all Marcas with pagination."""
    result = await db.execute(
        select(Marcas).offset(skip).limit(limit)
    )
    items = result.scalars().all()

    total_result = await db.execute(select(func.count(Marcas.id_marca)))
    total = total_result.scalar() or 0

    return MarcasListResponse(
        items=[MarcasResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{marca_id}", response_model=MarcasResponse)
async def get_marcas(
    marca_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> MarcasResponse:
    """Get a Marcas by ID."""
    result = await db.execute(
        select(Marcas).where(Marcas.id_marca == marca_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marcas not found")
    return MarcasResponse.model_validate(item)


@router.post("", response_model=MarcasResponse, status_code=status.HTTP_201_CREATED)
async def create_marcas(
    request: CreateMarcasRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> MarcasResponse:
    """Create a new Marcas (admin only)."""
    item = Marcas(nombre=request.nombre)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return MarcasResponse.model_validate(item)


@router.put("/{marca_id}", response_model=MarcasResponse)
async def update_marcas(
    marca_id: int,
    request: UpdateMarcasRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> MarcasResponse:
    """Update a Marcas (admin only)."""
    result = await db.execute(
        select(Marcas).where(Marcas.id_marca == marca_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marcas not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return MarcasResponse.model_validate(item)


@router.delete("/{marca_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_marcas(
    marca_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a Marcas (admin only)."""
    result = await db.execute(
        select(Marcas).where(Marcas.id_marca == marca_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marcas not found")

    await db.delete(item)
    return None
