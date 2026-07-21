"""Clientes DTOs (Pydantic models) for the new integer-PK Clientes table."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateClientesRequest(BaseModel):
    """Request model for creating a Clientes."""
    tipo_cliente: str = Field(..., max_length=20, description="Tipo de cliente: fisica o juridica")
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del cliente")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono")
    email: Optional[str] = Field(None, max_length=150, description="Email")
    razon_social: Optional[str] = Field(None, max_length=200, description="Razón social")
    cuit: Optional[str] = Field(None, max_length=20, description="CUIT")
    obra_social: Optional[str] = Field(None, max_length=200, description="Obra social")
    direccion: Optional[str] = Field(None, max_length=300, description="Dirección")
    localidad: Optional[str] = Field(None, max_length=100, description="Localidad")
    dni: Optional[str] = Field(None, max_length=20, description="DNI")


class UpdateClientesRequest(BaseModel):
    """Request model for updating a Clientes (all fields optional)."""
    tipo_cliente: Optional[str] = Field(None, max_length=20, description="Tipo de cliente")
    nombre: Optional[str] = Field(None, min_length=1, max_length=200, description="Nombre del cliente")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono")
    email: Optional[str] = Field(None, max_length=150, description="Email")
    razon_social: Optional[str] = Field(None, max_length=200, description="Razón social")
    cuit: Optional[str] = Field(None, max_length=20, description="CUIT")
    obra_social: Optional[str] = Field(None, max_length=200, description="Obra social")
    direccion: Optional[str] = Field(None, max_length=300, description="Dirección")
    localidad: Optional[str] = Field(None, max_length=100, description="Localidad")
    dni: Optional[str] = Field(None, max_length=20, description="DNI")


class ClientesResponse(BaseModel):
    """Response model for Clientes data."""
    id_cliente: int = Field(..., description="ID del cliente")
    tipo_cliente: str = Field(..., description="Tipo de cliente")
    nombre: str = Field(..., description="Nombre del cliente")
    telefono: Optional[str] = Field(None, description="Teléfono")
    email: Optional[str] = Field(None, description="Email")
    razon_social: Optional[str] = Field(None, description="Razón social")
    cuit: Optional[str] = Field(None, description="CUIT")
    obra_social: Optional[str] = Field(None, description="Obra social")
    direccion: Optional[str] = Field(None, description="Dirección")
    localidad: Optional[str] = Field(None, description="Localidad")
    dni: Optional[str] = Field(None, description="DNI")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")

    class Config:
        """Pydantic config."""
        from_attributes = True


class ClientesListResponse(BaseModel):
    """Paginated list of Clientes."""
    items: List[ClientesResponse] = Field(..., description="Lista de clientes")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
