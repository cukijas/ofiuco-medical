"""OrdenesServicio DTOs (Pydantic models) for the new integer-PK table."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateOrdenesServicioRequest(BaseModel):
    """Request model for creating an OrdenesServicio."""
    numero_orden: str = Field(..., max_length=10, description="Número de orden único")
    numero_referencia: str = Field(..., max_length=20, description="Número de referencia único")
    id_cliente: int = Field(..., description="ID del cliente")
    id_equipo: int = Field(..., description="ID del equipo")
    id_empleado: int = Field(..., description="ID del empleado")
    id_departamento: Optional[int] = Field(None, description="ID del departamento")
    solicitado_por: str = Field(..., max_length=200, description="Solicitado por")
    tipo_visita: str = Field(..., max_length=30, description="Tipo de visita: normal, por contrato, por garantia")
    condicion_equipo: str = Field(..., max_length=20, description="Condición del equipo: nuevo, usado, otro")
    accesorios: Optional[str] = Field(None, description="Accesorios")
    fecha_realizacion: date = Field(..., description="Fecha de realización")
    fecha_finalizacion: Optional[date] = Field(None, description="Fecha de finalización")
    tarea_realizada: Optional[str] = Field(None, description="Tarea realizada")
    horas_trabajo: Optional[Decimal] = Field(None, ge=0, description="Horas de trabajo")
    falla_detectada: Optional[str] = Field(None, description="Falla detectada")
    empleados_adicionales: Optional[str] = Field(None, description="IDs de empleados adicionales separados por coma")
    kilometros: Optional[Decimal] = Field(None, description="Kilómetros recorridos")
    viaticos: Optional[Decimal] = Field(None, description="Viáticos")
    configuracion_equipo: Optional[str] = Field(None, max_length=50, description="Configuración del equipo (ej: Rodante, Rodante c/Seriografo, Fijo)")
    qr_identifier: Optional[str] = Field(None, max_length=255, description="Identificador QR único (se genera automáticamente si no se provee)")
    onedrive_path: Optional[str] = Field(None, max_length=500, description="Ruta OneDrive")


class UpdateOrdenesServicioRequest(BaseModel):
    """Request model for updating an OrdenesServicio (all fields optional)."""
    numero_orden: Optional[str] = Field(None, max_length=10, description="Número de orden")
    numero_referencia: Optional[str] = Field(None, max_length=20, description="Número de referencia")
    id_cliente: Optional[int] = Field(None, description="ID del cliente")
    id_equipo: Optional[int] = Field(None, description="ID del equipo")
    id_empleado: Optional[int] = Field(None, description="ID del empleado")
    id_departamento: Optional[int] = Field(None, description="ID del departamento")
    solicitado_por: Optional[str] = Field(None, max_length=200, description="Solicitado por")
    tipo_visita: Optional[str] = Field(None, max_length=30, description="Tipo de visita")
    condicion_equipo: Optional[str] = Field(None, max_length=20, description="Condición del equipo")
    accesorios: Optional[str] = Field(None, description="Accesorios")
    fecha_realizacion: Optional[date] = Field(None, description="Fecha de realización")
    fecha_finalizacion: Optional[date] = Field(None, description="Fecha de finalización")
    tarea_realizada: Optional[str] = Field(None, description="Tarea realizada")
    horas_trabajo: Optional[Decimal] = Field(None, ge=0, description="Horas de trabajo")
    falla_detectada: Optional[str] = Field(None, description="Falla detectada")
    empleados_adicionales: Optional[str] = Field(None, description="IDs de empleados adicionales separados por coma")
    kilometros: Optional[Decimal] = Field(None, description="Kilómetros recorridos")
    viaticos: Optional[Decimal] = Field(None, description="Viáticos")
    configuracion_equipo: Optional[str] = Field(None, max_length=50, description="Configuración del equipo")
    onedrive_path: Optional[str] = Field(None, max_length=500, description="Ruta OneDrive")


class OrdenesServicioResponse(BaseModel):
    """Response model for OrdenesServicio data."""
    id_orden: int = Field(..., description="ID de la orden")
    numero_orden: str = Field(..., description="Número de orden")
    numero_referencia: str = Field(..., description="Número de referencia")
    id_cliente: int = Field(..., description="ID del cliente")
    id_equipo: int = Field(..., description="ID del equipo")
    id_empleado: int = Field(..., description="ID del empleado")
    id_departamento: Optional[int] = Field(None, description="ID del departamento")
    solicitado_por: str = Field(..., description="Solicitado por")
    tipo_visita: str = Field(..., description="Tipo de visita")
    condicion_equipo: str = Field(..., description="Condición del equipo")
    accesorios: Optional[str] = Field(None, description="Accesorios")
    fecha_realizacion: date = Field(..., description="Fecha de realización")
    fecha_finalizacion: Optional[date] = Field(None, description="Fecha de finalización")
    tarea_realizada: Optional[str] = Field(None, description="Tarea realizada")
    horas_trabajo: Optional[Decimal] = Field(None, description="Horas de trabajo")
    falla_detectada: Optional[str] = Field(None, description="Falla detectada")
    empleados_adicionales: Optional[str] = Field(None, description="Empleados adicionales")
    kilometros: Optional[Decimal] = Field(None, description="Kilómetros recorridos")
    viaticos: Optional[Decimal] = Field(None, description="Viáticos")
    configuracion_equipo: Optional[str] = Field(None, description="Configuración del equipo")
    qr_identifier: str = Field(..., description="Identificador QR")
    onedrive_path: Optional[str] = Field(None, description="Ruta OneDrive")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")

    class Config:
        """Pydantic config."""
        from_attributes = True


class OrdenesServicioListResponse(BaseModel):
    """Paginated list of OrdenesServicio."""
    items: List[OrdenesServicioResponse] = Field(..., description="Lista de órdenes de servicio")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
