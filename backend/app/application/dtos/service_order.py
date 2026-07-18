"""Service order DTOs (Pydantic models)."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class PartRequest(BaseModel):
    """Request model for adding a part to an order."""
    part_name: str = Field(..., min_length=1, max_length=255, description="Part name")
    part_number: Optional[str] = Field(None, max_length=255, description="Part number / SKU")
    quantity: int = Field(1, ge=1, description="Quantity of this part")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Cost per unit")


class PartResponse(BaseModel):
    """Response model for a part attached to an order."""
    id: uuid.UUID = Field(..., description="Part ID")
    service_order_id: uuid.UUID = Field(..., description="Parent order ID")
    part_name: str = Field(..., description="Part name")
    part_number: Optional[str] = Field(None, description="Part number / SKU")
    quantity: int = Field(..., description="Quantity")
    unit_cost: Optional[Decimal] = Field(None, description="Cost per unit")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class CreateOrderRequest(BaseModel):
    """Request model for creating a service order."""
    client_id: uuid.UUID = Field(..., description="Client UUID")
    equipment_id: uuid.UUID = Field(..., description="Equipment UUID")
    technician_id: Optional[uuid.UUID] = Field(
        None, description="Technician UUID (auto-assigned to current user if omitted)"
    )
    description: Optional[str] = Field(None, description="Service description")
    service_date: Optional[date] = Field(None, description="Scheduled service date")


class UpdateOrderRequest(BaseModel):
    """Request model for updating a service order (all fields optional)."""
    client_id: Optional[uuid.UUID] = Field(None, description="Client UUID")
    equipment_id: Optional[uuid.UUID] = Field(None, description="Equipment UUID")
    technician_id: Optional[uuid.UUID] = Field(None, description="Technician UUID")
    description: Optional[str] = Field(None, description="Service description")
    diagnosis: Optional[str] = Field(None, description="Technician diagnosis")
    solution: Optional[str] = Field(None, description="Solution applied")
    service_date: Optional[date] = Field(None, description="Scheduled service date")
    next_service_date: Optional[date] = Field(None, description="Next service date")


class UpdateStatusRequest(BaseModel):
    """Request model for updating service order status."""
    status: str = Field(..., description="New status: in_progress, completed, delivered")


class OrderResponse(BaseModel):
    """Response model for service order data."""
    id: uuid.UUID = Field(..., description="Order ID")
    order_number: str = Field(..., description="Unique order number (OS-XXXXD)")
    client_id: uuid.UUID = Field(..., description="Client UUID")
    equipment_id: uuid.UUID = Field(..., description="Equipment UUID")
    technician_id: uuid.UUID = Field(..., description="Technician UUID")
    status: str = Field(..., description="Order status")
    description: Optional[str] = Field(None, description="Service description")
    diagnosis: Optional[str] = Field(None, description="Technician diagnosis")
    solution: Optional[str] = Field(None, description="Solution applied")
    service_date: Optional[date] = Field(None, description="Scheduled service date")
    next_service_date: Optional[date] = Field(None, description="Next service date")
    is_active: bool = Field(..., description="Order active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    parts: list[PartResponse] = Field(default_factory=list, description="Spare parts used")

    class Config:
        """Pydantic config."""
        from_attributes = True


class OrderListResponse(BaseModel):
    """Paginated list of service orders."""
    items: list[OrderResponse] = Field(..., description="List of service orders")
    total: int = Field(..., description="Total matching orders")
    skip: int = Field(..., description="Offset used")
    limit: int = Field(..., description="Page size used")
