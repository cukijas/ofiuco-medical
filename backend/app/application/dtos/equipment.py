"""Equipment DTOs (Pydantic models)."""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class CreateEquipmentRequest(BaseModel):
    """Request model for creating equipment."""
    client_id: uuid.UUID = Field(..., description="Client UUID")
    category_id: uuid.UUID = Field(..., description="Category UUID")
    subcategory_id: Optional[uuid.UUID] = Field(None, description="Subcategory UUID")
    brand: str = Field(..., min_length=1, max_length=255, description="Equipment brand")
    model: str = Field(..., min_length=1, max_length=255, description="Equipment model")
    serial_number: str = Field(..., min_length=1, max_length=255, description="Serial number (unique)")


class UpdateEquipmentRequest(BaseModel):
    """Request model for updating equipment (all fields optional)."""
    client_id: Optional[uuid.UUID] = Field(None, description="Client UUID")
    category_id: Optional[uuid.UUID] = Field(None, description="Category UUID")
    subcategory_id: Optional[uuid.UUID] = Field(None, description="Subcategory UUID")
    brand: Optional[str] = Field(None, min_length=1, max_length=255, description="Equipment brand")
    model: Optional[str] = Field(None, min_length=1, max_length=255, description="Equipment model")
    serial_number: Optional[str] = Field(None, min_length=1, max_length=255, description="Serial number")
    onedrive_path: Optional[str] = Field(None, max_length=500, description="OneDrive folder path")


class EquipmentResponse(BaseModel):
    """Response model for equipment data."""
    id: uuid.UUID = Field(..., description="Equipment ID")
    client_id: uuid.UUID = Field(..., description="Client UUID")
    category_id: uuid.UUID = Field(..., description="Category UUID")
    subcategory_id: Optional[uuid.UUID] = Field(None, description="Subcategory UUID")
    category_name: Optional[str] = Field(None, description="Category name (resolved)")
    subcategory_name: Optional[str] = Field(None, description="Subcategory name (resolved)")
    brand: str = Field(..., description="Equipment brand")
    model: str = Field(..., description="Equipment model")
    serial_number: str = Field(..., description="Serial number")
    qr_code: str = Field(..., description="QR code token")
    onedrive_path: Optional[str] = Field(None, description="OneDrive folder path")
    is_active: bool = Field(..., description="Equipment active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class EquipmentListResponse(BaseModel):
    """Paginated list of equipment."""
    items: list[EquipmentResponse] = Field(..., description="List of equipment")
    total: int = Field(..., description="Total number of active equipment")
    skip: int = Field(..., description="Offset used")
    limit: int = Field(..., description="Page size used")
