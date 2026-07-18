"""Category repository implementation."""

from typing import List, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.category import Category
from backend.app.domain.models.subcategory import Subcategory
from backend.app.domain.ports.category_repo import ICategoryRepo


class CategoryRepo(ICategoryRepo):
    """SQLAlchemy implementation of category repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ─── Category methods ──────────────────────────────────────────────────

    async def create(self, category: Category) -> Category:
        """Create a new category."""
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        """Get category by ID."""
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        result = await self.session.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all active categories with pagination."""
        result = await self.session.execute(
            select(Category)
            .where(Category.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Count total active categories."""
        result = await self.session.execute(
            select(func.count(Category.id)).where(Category.is_active == True)
        )
        return result.scalar() or 0

    async def update(self, category: Category) -> Category:
        """Update an existing category."""
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category_id: uuid.UUID) -> bool:
        """Soft delete a category."""
        category = await self.get_by_id(category_id)
        if category:
            category.is_active = False
            await self.session.flush()
            return True
        return False

    # ─── Subcategory methods ───────────────────────────────────────────────

    async def create_subcategory(self, subcategory: Subcategory) -> Subcategory:
        """Create a new subcategory."""
        self.session.add(subcategory)
        await self.session.flush()
        await self.session.refresh(subcategory)
        return subcategory

    async def get_subcategory_by_id(self, subcategory_id: uuid.UUID) -> Optional[Subcategory]:
        """Get subcategory by ID."""
        result = await self.session.execute(
            select(Subcategory).where(Subcategory.id == subcategory_id)
        )
        return result.scalar_one_or_none()

    async def get_subcategories_by_category(
        self, category_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Subcategory]:
        """Get all active subcategories for a category."""
        result = await self.session.execute(
            select(Subcategory)
            .where(Subcategory.category_id == category_id, Subcategory.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_subcategories_by_category(self, category_id: uuid.UUID) -> int:
        """Count active subcategories for a category."""
        result = await self.session.execute(
            select(func.count(Subcategory.id)).where(
                Subcategory.category_id == category_id,
                Subcategory.is_active == True,
            )
        )
        return result.scalar() or 0

    async def update_subcategory(self, subcategory: Subcategory) -> Subcategory:
        """Update an existing subcategory."""
        await self.session.flush()
        await self.session.refresh(subcategory)
        return subcategory

    async def delete_subcategory(self, subcategory_id: uuid.UUID) -> bool:
        """Soft delete a subcategory."""
        subcategory = await self.get_subcategory_by_id(subcategory_id)
        if subcategory:
            subcategory.is_active = False
            await self.session.flush()
            return True
        return False