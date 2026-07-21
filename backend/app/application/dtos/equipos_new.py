"""Equipos DTOs (Pydantic models) for the new integer-PK Equipos table."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateEquiposRequest(BaseModel):
    """Request model for creating an Equipos."""
    id_tipo_equipos: int = Field(..., description="ID del tipo de equipo")
    id_marca: int = Field(..., description="ID de la marca")
    modelo: str = Field(..., min_length=1, max_length=150, description="Modelo del equipo")
    id_cliente: int = Field(..., description="ID del cliente")
    numero_serie: Optional[str] = Field(None, max_length=100, description="Número de serie")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción")
    condicion: str = Field("usado", max_length=20, description="Condición: nuevo, usado, otro")
    accesorios: Optional[str] = Field(None, description="Accesorios")
    qr_identifier: Optional[str] = Field(None, max_length=255, description="Identificador QR único (se genera automáticamente si no se provee)")
    onedrive_path: Optional[str] = Field(None, max_length=500, description="Ruta OneDrive")
    id_subtipo: Optional[int] = Field(None, description="ID del subtipo de equipo")


class UpdateEquiposRequest(BaseModel):
    """Request model for updating an Equipos (all fields optional)."""
    id_tipo_equipos: Optional[int] = Field(None, description="ID del tipo de equipo")
    id_marca: Optional[int] = Field(None, description="ID de la marca")
    modelo: Optional[str] = Field(None, min_length=1, max_length=150, description="Modelo del equipo")
    id_cliente: Optional[int] = Field(None, description="ID del cliente")
    numero_serie: Optional[str] = Field(None, max_length=100, description="Número de serie")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción")
    condicion: Optional[str] = Field(None, max_length=20, description="Condición")
    accesorios: Optional[str] = Field(None, description="Accesorios")
    onedrive_path: Optional[str] = Field(None, max_length=500, description="Ruta OneDrive")
    id_subtipo: Optional[int] = Field(None, description="ID del subtipo de equipo")


class EquiposResponse(BaseModel):
    """Response model for Equipos data."""
    id_equipos: int = Field(..., description="ID del equipo")
    id_tipo_equipos: int = Field(..., description="ID del tipo de equipo")
    id_marca: int = Field(..., description="ID de la marca")
    modelo: str = Field(..., description="Modelo del equipo")
    id_cliente: int = Field(..., description="ID del cliente")
    numero_serie: Optional[str] = Field(None, description="Número de serie")
    descripcion: Optional[str] = Field(None, description="Descripción")
    condicion: str = Field(..., description="Condición")
    accesorios: Optional[str] = Field(None, description="Accesorios")
    qr_identifier: str = Field(..., description="Identificador QR")
    onedrive_path: Optional[str] = Field(None, description="Ruta OneDrive")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")

    class Config:
        """Pydantic config."""
        from_attributes = True


class EquiposListResponse(BaseModel):
    """Paginated list of Equipos."""
    items: List[EquiposResponse] = Field(..., description="Lista de equipos")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
