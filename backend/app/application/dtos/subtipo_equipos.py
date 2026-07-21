"""SubtipoEquipos DTOs (Pydantic models)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CreateSubtipoEquiposRequest(BaseModel):
    """Request model for creating a SubtipoEquipos."""
    id_tipo_equipos: int = Field(..., description="ID del tipo de equipo padre")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del subtipo")


class UpdateSubtipoEquiposRequest(BaseModel):
    """Request model for updating a SubtipoEquipos (all fields optional)."""
    id_tipo_equipos: Optional[int] = Field(None, description="ID del tipo de equipo padre")
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del subtipo")


class SubtipoEquiposResponse(BaseModel):
    """Response model for SubtipoEquipos data."""
    id_subtipo: int = Field(..., description="ID del subtipo")
    id_tipo_equipos: int = Field(..., description="ID del tipo de equipo padre")
    nombre: str = Field(..., description="Nombre del subtipo")

    class Config:
        """Pydantic config."""
        from_attributes = True


class SubtipoEquiposListResponse(BaseModel):
    """Paginated list of SubtipoEquipos."""
    items: List[SubtipoEquiposResponse] = Field(..., description="Lista de subtipos")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
