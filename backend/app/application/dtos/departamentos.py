"""Departamentos DTOs (Pydantic models)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CreateDepartamentosRequest(BaseModel):
    """Request model for creating a Departamentos."""
    id_cliente: int = Field(..., description="ID del cliente padre")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del departamento")


class UpdateDepartamentosRequest(BaseModel):
    """Request model for updating a Departamentos (all fields optional)."""
    id_cliente: Optional[int] = Field(None, description="ID del cliente padre")
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del departamento")


class DepartamentosResponse(BaseModel):
    """Response model for Departamentos data."""
    id_departamento: int = Field(..., description="ID del departamento")
    id_cliente: int = Field(..., description="ID del cliente padre")
    nombre: str = Field(..., description="Nombre del departamento")

    class Config:
        """Pydantic config."""
        from_attributes = True


class DepartamentosListResponse(BaseModel):
    """Paginated list of Departamentos."""
    items: List[DepartamentosResponse] = Field(..., description="Lista de departamentos")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
