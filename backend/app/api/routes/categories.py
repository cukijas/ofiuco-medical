"""Category and Subcategory API routes."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.category import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
    CategoryResponse,
    CategoryListResponse,
    CreateSubcategoryRequest,
    UpdateSubcategoryRequest,
    SubcategoryResponse,
    SubcategoryListResponse,
)
from backend.app.application.services.category_service import CategoryService
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.database.category_repo_impl import CategoryRepo
from backend.app.domain.models.user import User

router = APIRouter(prefix="/categories", tags=["categories"])


def _build_service(db: AsyncSession) -> CategoryService:
    """Create CategoryService with its repository dependencies."""
    repo = CategoryRepo(db)
    return CategoryService(repo)


# ─── Category Endpoints ───────────────────────────────────────────────────────

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    request: CreateCategoryRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Create a new category (admin only).

    Args:
        request: Category creation data.
        current_user: Authenticated admin.
        db: Database session.

    Returns:
        Created category data.
    """
    service = _build_service(db)
    return await service.create(request)


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> CategoryListResponse:
    """List categories with pagination.

    Args:
        skip: Offset for pagination.
        limit: Maximum items per page.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Paginated list of categories.
    """
    service = _build_service(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Get a category by ID.

    Args:
        category_id: UUID of the category.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Category data.
    """
    service = _build_service(db)
    return await service.get_by_id(category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    request: UpdateCategoryRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Update a category (admin only, partial update).

    Args:
        category_id: UUID of the category to update.
        request: Fields to update.
        current_user: Authenticated admin.
        db: Database session.

    Returns:
        Updated category data.
    """
    service = _build_service(db)
    return await service.update(category_id, request)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a category (admin only).

    Args:
        category_id: UUID of the category to delete.
        current_user: Authenticated admin.
        db: Database session.
    """
    service = _build_service(db)
    await service.delete(category_id)
    return None


# ─── Subcategory Endpoints ────────────────────────────────────────────────────

@router.post(
    "/{category_id}/subcategories",
    response_model=SubcategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subcategory(
    category_id: uuid.UUID,
    request: CreateSubcategoryRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> SubcategoryResponse:
    """Create a new subcategory under a category (admin only).

    The category_id in the URL path is used as the parent; any category_id
    in the request body is ignored.

    Args:
        category_id: UUID of the parent category (from URL path).
        request: Subcategory creation data (name only).
        current_user: Authenticated admin.
        db: Database session.

    Returns:
        Created subcategory data.
    """
    service = _build_service(db)
    return await service.create_subcategory(category_id=category_id, request=request)


@router.get("/{category_id}/subcategories", response_model=SubcategoryListResponse)
async def list_subcategories(
    category_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Page size"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> SubcategoryListResponse:
    """List active subcategories for a specific category.

    Args:
        category_id: UUID of the parent category.
        skip: Offset for pagination.
        limit: Maximum items per page.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Paginated list of subcategories.
    """
    service = _build_service(db)
    return await service.get_subcategories_by_category(
        category_id=category_id, skip=skip, limit=limit
    )


@router.get("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
async def get_subcategory(
    subcategory_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> SubcategoryResponse:
    """Get a subcategory by ID.

    Args:
        subcategory_id: UUID of the subcategory.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Subcategory data.
    """
    service = _build_service(db)
    return await service.get_subcategory_by_id(subcategory_id)


@router.put("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
async def update_subcategory(
    subcategory_id: uuid.UUID,
    request: UpdateSubcategoryRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> SubcategoryResponse:
    """Update a subcategory (admin only, partial update).

    Args:
        subcategory_id: UUID of the subcategory to update.
        request: Fields to update.
        current_user: Authenticated admin.
        db: Database session.

    Returns:
        Updated subcategory data.
    """
    service = _build_service(db)
    return await service.update_subcategory(subcategory_id, request)


@router.delete("/subcategories/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subcategory(
    subcategory_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a subcategory (admin only).

    Args:
        subcategory_id: UUID of the subcategory to delete.
        current_user: Authenticated admin.
        db: Database session.
    """
    service = _build_service(db)
    await service.delete_subcategory(subcategory_id)
    return None