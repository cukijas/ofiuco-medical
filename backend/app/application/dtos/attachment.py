"""Attachment DTOs (Pydantic models)."""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    """Response model for attachment data."""
    id: uuid.UUID = Field(..., description="Attachment ID")
    file_name: str = Field(..., description="File name")
    file_type: str = Field(..., description="File type (report, photo, manual, other)")
    onedrive_path: Optional[str] = Field(None, description="OneDrive storage path")
    uploaded_by: uuid.UUID = Field(..., description="User ID of uploader")
    equipment_id: Optional[uuid.UUID] = Field(None, description="Related equipment ID")
    service_order_id: Optional[uuid.UUID] = Field(None, description="Related service order ID")
    is_active: bool = Field(..., description="Attachment active status")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class AttachmentListResponse(BaseModel):
    """Paginated list of attachments."""
    items: list[AttachmentResponse] = Field(..., description="List of attachments")
    total: int = Field(..., description="Total matching attachments")
