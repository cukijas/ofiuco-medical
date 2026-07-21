"""Equipos API routes for the new integer-PK Equipos table."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.equipos_new import (
    CreateEquiposRequest,
    UpdateEquiposRequest,
    EquiposResponse,
    EquiposListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.equipos import Equipos
from backend.app.domain.models.equipos_subtipos import EquiposSubtipos
from backend.app.domain.models.subtipo_equipos import SubtipoEquipos
from backend.app.domain.models.tipo_equipos import TipoEquipos
from backend.app.domain.models.marcas import Marcas
from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.user import User

router = APIRouter(prefix="/equipos", tags=["equipos"])


@router.get("", response_model=EquiposListResponse)
async def list_equipos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    id_cliente: int | None = Query(None, description="Filter by cliente ID"),
    id_tipo_equipos: int | None = Query(None, description="Filter by tipo equipo ID"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquiposListResponse:
    """List all Equipos with optional filters and pagination."""
    query = select(Equipos)
    count_query = select(func.count(Equipos.id_equipos))

    if id_cliente is not None:
        query = query.where(Equipos.id_cliente == id_cliente)
        count_query = count_query.where(Equipos.id_cliente == id_cliente)
    if id_tipo_equipos is not None:
        query = query.where(Equipos.id_tipo_equipos == id_tipo_equipos)
        count_query = count_query.where(Equipos.id_tipo_equipos == id_tipo_equipos)

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return EquiposListResponse(
        items=[EquiposResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{equipo_id}", response_model=EquiposResponse)
async def get_equipos(
    equipo_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquiposResponse:
    """Get an Equipos by ID."""
    result = await db.execute(
        select(Equipos).where(Equipos.id_equipos == equipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipos not found")
    return EquiposResponse.model_validate(item)


@router.post("", response_model=EquiposResponse, status_code=status.HTTP_201_CREATED)
async def create_equipos(
    request: CreateEquiposRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquiposResponse:
    """Create a new Equipos."""
    for model, field_name, col_name in [
        (TipoEquipos, "id_tipo_equipos", "id_tipo_equipos"),
        (Marcas, "id_marca", "id_marca"),
        (Clientes, "id_cliente", "id_cliente"),
    ]:
        fk_val = getattr(request, field_name)
        col = getattr(model, col_name)
        ref = await db.execute(select(model).where(col == fk_val))
        if not ref.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{field_name} not found")

    item = Equipos(
        id_tipo_equipos=request.id_tipo_equipos,
        id_marca=request.id_marca,
        modelo=request.modelo,
        id_cliente=request.id_cliente,
        numero_serie=request.numero_serie,
        descripcion=request.descripcion,
        condicion=request.condicion,
        accesorios=request.accesorios,
        qr_identifier=request.qr_identifier or str(uuid.uuid4()),
        onedrive_path=request.onedrive_path,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)

    # Handle subtipo relationship
    if request.id_subtipo is not None:
        subtipo_result = await db.execute(
            select(SubtipoEquipos).where(
                SubtipoEquipos.id_subtipo == request.id_subtipo,
                SubtipoEquipos.id_tipo_equipos == request.id_tipo_equipos,
            )
        )
        if not subtipo_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Subtipo does not belong to the selected tipo")

        junction = EquiposSubtipos(id_equipos=item.id_equipos, id_subtipo=request.id_subtipo)
        db.add(junction)
        await db.flush()

    return EquiposResponse.model_validate(item)


@router.put("/{equipo_id}", response_model=EquiposResponse)
async def update_equipos(
    equipo_id: int,
    request: UpdateEquiposRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> EquiposResponse:
    """Update an Equipos (partial update)."""
    result = await db.execute(
        select(Equipos).where(Equipos.id_equipos == equipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipos not found")

    update_data = request.model_dump(exclude_unset=True)

    # Handle subtipo update separately (not a column on Equipos)
    subtipo_id = update_data.pop("id_subtipo", None)
    subtipo_sent = "id_subtipo" in request.model_fields_set

    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()

    if subtipo_sent:
        # Delete existing junction rows
        existing = await db.execute(
            select(EquiposSubtipos).where(EquiposSubtipos.id_equipos == equipo_id)
        )
        for junction in existing.scalars().all():
            await db.delete(junction)

        # Add new junction if subtipo is provided
        if subtipo_id is not None:
            tipo_id = update_data.get("id_tipo_equipos", item.id_tipo_equipos)
            subtipo_result = await db.execute(
                select(SubtipoEquipos).where(
                    SubtipoEquipos.id_subtipo == subtipo_id,
                    SubtipoEquipos.id_tipo_equipos == tipo_id,
                )
            )
            if not subtipo_result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Subtipo does not belong to the selected tipo")

            junction = EquiposSubtipos(id_equipos=equipo_id, id_subtipo=subtipo_id)
            db.add(junction)

        await db.flush()

    await db.refresh(item)
    return EquiposResponse.model_validate(item)


@router.get("/{equipo_id}/subtipo")
async def get_equipo_subtipo(
    equipo_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
):
    """Get the subtipo for a given equipo."""
    result = await db.execute(
        select(SubtipoEquipos)
        .join(EquiposSubtipos, EquiposSubtipos.id_subtipo == SubtipoEquipos.id_subtipo)
        .where(EquiposSubtipos.id_equipos == equipo_id)
    )
    subtipo = result.scalar_one_or_none()
    if not subtipo:
        return {"id_subtipo": None, "nombre": None}
    return {"id_subtipo": subtipo.id_subtipo, "nombre": subtipo.nombre}


@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipos(
    equipo_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an Equipos (admin only)."""
    result = await db.execute(
        select(Equipos).where(Equipos.id_equipos == equipo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipos not found")

    await db.delete(item)
    return None
