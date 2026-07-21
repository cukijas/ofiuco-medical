"""Empleados DTOs (Pydantic models)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateEmpleadosRequest(BaseModel):
    """Request model for creating an Empleados."""
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del empleado")
    especialidad: Optional[str] = Field(None, max_length=100, description="Especialidad")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono")
    email: Optional[str] = Field(None, max_length=150, description="Email")
    activo: bool = Field(True, description="Estado activo")


class UpdateEmpleadosRequest(BaseModel):
    """Request model for updating an Empleados (all fields optional)."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200, description="Nombre del empleado")
    especialidad: Optional[str] = Field(None, max_length=100, description="Especialidad")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono")
    email: Optional[str] = Field(None, max_length=150, description="Email")
    activo: Optional[bool] = Field(None, description="Estado activo")


class EmpleadosResponse(BaseModel):
    """Response model for Empleados data."""
    id_empleado: int = Field(..., description="ID del empleado")
    nombre: str = Field(..., description="Nombre del empleado")
    especialidad: Optional[str] = Field(None, description="Especialidad")
    telefono: Optional[str] = Field(None, description="Teléfono")
    email: Optional[str] = Field(None, description="Email")
    activo: bool = Field(..., description="Estado activo")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")

    class Config:
        """Pydantic config."""
        from_attributes = True


class EmpleadosListResponse(BaseModel):
    """Paginated list of Empleados."""
    items: List[EmpleadosResponse] = Field(..., description="Lista de empleados")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
