"""TipoEquipos DTOs (Pydantic models)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CreateTipoEquiposRequest(BaseModel):
    """Request model for creating a TipoEquipos."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del tipo de equipo")


class UpdateTipoEquiposRequest(BaseModel):
    """Request model for updating a TipoEquipos (all fields optional)."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del tipo de equipo")


class TipoEquiposResponse(BaseModel):
    """Response model for TipoEquipos data."""
    id_tipo_equipos: int = Field(..., description="ID del tipo de equipo")
    nombre: str = Field(..., description="Nombre del tipo de equipo")

    class Config:
        """Pydantic config."""
        from_attributes = True


class TipoEquiposListResponse(BaseModel):
    """Paginated list of TipoEquipos."""
    items: List[TipoEquiposResponse] = Field(..., description="Lista de tipos de equipo")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
