"""Category application service."""

import uuid

from fastapi import HTTPException, status

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
from backend.app.domain.models.category import Category
from backend.app.domain.models.subcategory import Subcategory
from backend.app.domain.ports.category_repo import ICategoryRepo


class CategoryService:
    """Service layer for category CRUD operations."""

    def __init__(self, category_repo: ICategoryRepo) -> None:
        self.category_repo = category_repo

    async def create(self, request: CreateCategoryRequest) -> CategoryResponse:
        """Create a new category.

        Args:
            request: Category creation data.

        Returns:
            Created category response.

        Raises:
            HTTPException 409: If category name already exists.
        """
        existing = await self.category_repo.get_by_name(request.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with name '{request.name}' already exists",
            )

        category = Category(name=request.name)
        created = await self.category_repo.create(category)
        return CategoryResponse.model_validate(created)

    async def get_by_id(self, category_id: uuid.UUID) -> CategoryResponse:
        """Get a category by ID.

        Args:
            category_id: UUID of the category.

        Returns:
            Category response.

        Raises:
            HTTPException 404: If category not found.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return CategoryResponse.model_validate(category)

    async def get_all(self, skip: int = 0, limit: int = 20) -> CategoryListResponse:
        """List active categories with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Paginated category list.
        """
        categories = await self.category_repo.get_all(skip=skip, limit=limit)
        total = await self.category_repo.count_active()
        items = [CategoryResponse.model_validate(c) for c in categories if c.is_active]
        return CategoryListResponse(items=items, total=total, skip=skip, limit=limit)

    async def update(
        self,
        category_id: uuid.UUID,
        request: UpdateCategoryRequest,
    ) -> CategoryResponse:
        """Update a category (partial update).

        Args:
            category_id: UUID of the category to update.
            request: Fields to update (only non-None values applied).

        Returns:
            Updated category response.

        Raises:
            HTTPException 404: If category not found.
            HTTPException 409: If new name conflicts with another category.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        update_data = request.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != category.name:
            existing = await self.category_repo.get_by_name(update_data["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category with name '{update_data['name']}' already exists",
                )

        for field, value in update_data.items():
            setattr(category, field, value)

        updated = await self.category_repo.update(category)
        return CategoryResponse.model_validate(updated)

    async def delete(self, category_id: uuid.UUID) -> None:
        """Soft-delete a category.

        Args:
            category_id: UUID of the category to delete.

        Raises:
            HTTPException 404: If category not found.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        await self.category_repo.delete(category_id)

    # ─── Subcategory methods ──────────────────────────────────────────────

    async def create_subcategory(
        self,
        category_id: uuid.UUID,
        request: CreateSubcategoryRequest,
    ) -> SubcategoryResponse:
        """Create a new subcategory under an existing category.

        Args:
            category_id: UUID of the parent category.
            request: Subcategory creation data.

        Returns:
            Created subcategory response.

        Raises:
            HTTPException 404: If parent category not found.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

        subcategory = Subcategory(
            category_id=category_id,
            name=request.name,
        )
        created = await self.category_repo.create_subcategory(subcategory)
        return SubcategoryResponse.model_validate(created)

    async def get_subcategory_by_id(
        self,
        subcategory_id: uuid.UUID,
    ) -> SubcategoryResponse:
        """Get a subcategory by ID.

        Args:
            subcategory_id: UUID of the subcategory.

        Returns:
            Subcategory response.

        Raises:
            HTTPException 404: If subcategory not found.
        """
        subcategory = await self.category_repo.get_subcategory_by_id(subcategory_id)
        if not subcategory or not subcategory.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategory not found",
            )
        return SubcategoryResponse.model_validate(subcategory)

    async def get_subcategories_by_category(
        self,
        category_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> SubcategoryListResponse:
        """List active subcategories for a specific category.

        Args:
            category_id: UUID of the parent category.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Paginated subcategory list.

        Raises:
            HTTPException 404: If parent category not found.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

        subcategories = await self.category_repo.get_subcategories_by_category(
            category_id=category_id, skip=skip, limit=limit
        )
        total = await self.category_repo.count_subcategories_by_category(category_id)
        items = [SubcategoryResponse.model_validate(s) for s in subcategories if s.is_active]
        return SubcategoryListResponse(items=items, total=total, skip=skip, limit=limit)

    async def update_subcategory(
        self,
        subcategory_id: uuid.UUID,
        request: UpdateSubcategoryRequest,
    ) -> SubcategoryResponse:
        """Update a subcategory (partial update).

        Args:
            subcategory_id: UUID of the subcategory to update.
            request: Fields to update.

        Returns:
            Updated subcategory response.

        Raises:
            HTTPException 404: If subcategory or new parent category not found.
        """
        subcategory = await self.category_repo.get_subcategory_by_id(subcategory_id)
        if not subcategory or not subcategory.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategory not found",
            )

        update_data = request.model_dump(exclude_unset=True)

        # Validate new parent category if changing
        if "category_id" in update_data and update_data["category_id"] != subcategory.category_id:
            new_category = await self.category_repo.get_by_id(update_data["category_id"])
            if not new_category or not new_category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="New parent category not found",
                )

        for field, value in update_data.items():
            setattr(subcategory, field, value)

        updated = await self.category_repo.update_subcategory(subcategory)
        return SubcategoryResponse.model_validate(updated)

    async def delete_subcategory(self, subcategory_id: uuid.UUID) -> None:
        """Soft-delete a subcategory.

        Args:
            subcategory_id: UUID of the subcategory to delete.

        Raises:
            HTTPException 404: If subcategory not found.
        """
        subcategory = await self.category_repo.get_subcategory_by_id(subcategory_id)
        if not subcategory or not subcategory.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategory not found",
            )
        await self.category_repo.delete_subcategory(subcategory_id)