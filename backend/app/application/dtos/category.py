"""Category and Subcategory DTOs (Pydantic models)."""

from datetime import datetime
from typing import Optional, List
import uuid

from pydantic import BaseModel, Field


# ─── Category DTOs ────────────────────────────────────────────────────────────

class CreateCategoryRequest(BaseModel):
    """Request model for creating a category."""
    name: str = Field(..., min_length=1, max_length=255, description="Category name (unique)")


class UpdateCategoryRequest(BaseModel):
    """Request model for updating a category (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Category name")


class CategoryResponse(BaseModel):
    """Response model for category data."""
    id: uuid.UUID = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    is_active: bool = Field(..., description="Category active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Paginated list of categories."""
    items: List[CategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of active categories")
    skip: int = Field(..., description="Offset used")
    limit: int = Field(..., description="Page size used")


# ─── Subcategory DTOs ─────────────────────────────────────────────────────────

class CreateSubcategoryRequest(BaseModel):
    """Request model for creating a subcategory.

    Note: category_id is taken from the URL path, not the request body.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Subcategory name")


class UpdateSubcategoryRequest(BaseModel):
    """Request model for updating a subcategory (all fields optional)."""
    category_id: Optional[uuid.UUID] = Field(None, description="Parent category ID")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Subcategory name")


class SubcategoryResponse(BaseModel):
    """Response model for subcategory data."""
    id: uuid.UUID = Field(..., description="Subcategory ID")
    category_id: uuid.UUID = Field(..., description="Parent category ID")
    name: str = Field(..., description="Subcategory name")
    is_active: bool = Field(..., description="Subcategory active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class SubcategoryListResponse(BaseModel):
    """Paginated list of subcategories."""
    items: List[SubcategoryResponse] = Field(..., description="List of subcategories")
    total: int = Field(..., description="Total number of active subcategories")
    skip: int = Field(..., description="Offset used")
    limit: int = Field(..., description="Page size used")