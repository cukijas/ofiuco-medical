"""Client DTOs (Pydantic models)."""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, EmailStr, Field


class CreateClientRequest(BaseModel):
    """Request model for creating a client."""
    name: str = Field(..., min_length=1, max_length=255, description="Client company name (unique)")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, max_length=255, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=255, description="Physical address")
    city: Optional[str] = Field(None, max_length=255, description="City")
    province: Optional[str] = Field(None, max_length=255, description="Province or state")
    postal_code: Optional[str] = Field(None, max_length=255, description="Postal code")


class UpdateClientRequest(BaseModel):
    """Request model for updating a client (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Client company name")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, max_length=255, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=255, description="Physical address")
    city: Optional[str] = Field(None, max_length=255, description="City")
    province: Optional[str] = Field(None, max_length=255, description="Province or state")
    postal_code: Optional[str] = Field(None, max_length=255, description="Postal code")


class ClientResponse(BaseModel):
    """Response model for client data."""
    id: uuid.UUID = Field(..., description="Client ID")
    name: str = Field(..., description="Client company name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    address: Optional[str] = Field(None, description="Physical address")
    city: Optional[str] = Field(None, description="City")
    province: Optional[str] = Field(None, description="Province or state")
    postal_code: Optional[str] = Field(None, description="Postal code")
    is_active: bool = Field(..., description="Client active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class ClientListResponse(BaseModel):
    """Paginated list of clients."""
    items: list[ClientResponse] = Field(..., description="List of clients")
    total: int = Field(..., description="Total number of active clients")
    skip: int = Field(..., description="Offset used")
    limit: int = Field(..., description="Page size used")
