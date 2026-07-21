"""Marcas DTOs (Pydantic models)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CreateMarcasRequest(BaseModel):
    """Request model for creating a Marcas."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la marca")


class UpdateMarcasRequest(BaseModel):
    """Request model for updating a Marcas (all fields optional)."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la marca")


class MarcasResponse(BaseModel):
    """Response model for Marcas data."""
    id_marca: int = Field(..., description="ID de la marca")
    nombre: str = Field(..., description="Nombre de la marca")

    class Config:
        """Pydantic config."""
        from_attributes = True


class MarcasListResponse(BaseModel):
    """Paginated list of Marcas."""
    items: List[MarcasResponse] = Field(..., description="Lista de marcas")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Offset usado")
    limit: int = Field(..., description="Tamaño de página")
