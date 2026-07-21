"""OrdenesServicio API routes for the new integer-PK table."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.ordenes_servicio import (
    CreateOrdenesServicioRequest,
    UpdateOrdenesServicioRequest,
    OrdenesServicioResponse,
    OrdenesServicioListResponse,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.domain.models.ordenes_servicio import OrdenesServicio
from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.equipos import Equipos
from backend.app.domain.models.empleados import Empleados
from backend.app.domain.models.user import User

router = APIRouter(prefix="/ordenes-servicio", tags=["ordenes-servicio"])


@router.get("", response_model=OrdenesServicioListResponse)
async def list_ordenes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    id_cliente: Optional[int] = Query(None, description="Filter by cliente ID"),
    id_equipo: Optional[int] = Query(None, description="Filter by equipo ID"),
    id_empleado: Optional[int] = Query(None, description="Filter by empleado ID"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrdenesServicioListResponse:
    """List all OrdenesServicio with optional filters and pagination."""
    query = select(OrdenesServicio)
    count_query = select(func.count(OrdenesServicio.id_orden))

    if id_cliente is not None:
        query = query.where(OrdenesServicio.id_cliente == id_cliente)
        count_query = count_query.where(OrdenesServicio.id_cliente == id_cliente)
    if id_equipo is not None:
        query = query.where(OrdenesServicio.id_equipo == id_equipo)
        count_query = count_query.where(OrdenesServicio.id_equipo == id_equipo)
    if id_empleado is not None:
        query = query.where(OrdenesServicio.id_empleado == id_empleado)
        count_query = count_query.where(OrdenesServicio.id_empleado == id_empleado)

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return OrdenesServicioListResponse(
        items=[OrdenesServicioResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{orden_id}", response_model=OrdenesServicioResponse)
async def get_orden(
    orden_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrdenesServicioResponse:
    """Get an OrdenesServicio by ID."""
    result = await db.execute(
        select(OrdenesServicio).where(OrdenesServicio.id_orden == orden_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OrdenesServicio not found")
    return OrdenesServicioResponse.model_validate(item)


@router.post("", response_model=OrdenesServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_orden(
    request: CreateOrdenesServicioRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrdenesServicioResponse:
    """Create a new OrdenesServicio."""
    for model, field_name, col_name in [
        (Clientes, "id_cliente", "id_cliente"),
        (Equipos, "id_equipo", "id_equipos"),
        (Empleados, "id_empleado", "id_empleado"),
    ]:
        fk_val = getattr(request, field_name)
        col = getattr(model, col_name)
        ref = await db.execute(select(model).where(col == fk_val))
        if not ref.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{field_name} not found")

    item = OrdenesServicio(
        numero_orden=request.numero_orden,
        numero_referencia=request.numero_referencia,
        id_cliente=request.id_cliente,
        id_equipo=request.id_equipo,
        id_empleado=request.id_empleado,
        id_departamento=request.id_departamento,
        solicitado_por=request.solicitado_por,
        tipo_visita=request.tipo_visita,
        condicion_equipo=request.condicion_equipo,
        accesorios=request.accesorios,
        fecha_realizacion=request.fecha_realizacion,
        fecha_finalizacion=request.fecha_finalizacion,
        falla_detectada=request.falla_detectada,
        tarea_realizada=request.tarea_realizada,
        horas_trabajo=request.horas_trabajo,
        empleados_adicionales=request.empleados_adicionales,
        kilometros=request.kilometros,
        viaticos=request.viaticos,
        configuracion_equipo=request.configuracion_equipo,
        qr_identifier=request.qr_identifier or str(uuid.uuid4()),
        onedrive_path=request.onedrive_path,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return OrdenesServicioResponse.model_validate(item)


@router.put("/{orden_id}", response_model=OrdenesServicioResponse)
async def update_orden(
    orden_id: int,
    request: UpdateOrdenesServicioRequest,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> OrdenesServicioResponse:
    """Update an OrdenesServicio (partial update)."""
    result = await db.execute(
        select(OrdenesServicio).where(OrdenesServicio.id_orden == orden_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OrdenesServicio not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return OrdenesServicioResponse.model_validate(item)


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_orden(
    orden_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an OrdenesServicio (admin only)."""
    result = await db.execute(
        select(OrdenesServicio).where(OrdenesServicio.id_orden == orden_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OrdenesServicio not found")

    await db.delete(item)
    return None
