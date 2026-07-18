"""Category repository port."""

from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from backend.app.domain.models.category import Category
from backend.app.domain.models.subcategory import Subcategory


class ICategoryRepo(ABC):
    """Abstract category repository interface."""

    # ─── Category methods ──────────────────────────────────────────────────

    @abstractmethod
    async def create(self, category: Category) -> Category:
        """Create a new category."""
        ...

    @abstractmethod
    async def get_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        """Get category by ID."""
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all active categories with pagination."""
        ...

    @abstractmethod
    async def count_active(self) -> int:
        """Count total active categories."""
        ...

    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Update an existing category."""
        ...

    @abstractmethod
    async def delete(self, category_id: uuid.UUID) -> bool:
        """Soft delete a category."""
        ...

    # ─── Subcategory methods ───────────────────────────────────────────────

    @abstractmethod
    async def create_subcategory(self, subcategory: Subcategory) -> Subcategory:
        """Create a new subcategory."""
        ...

    @abstractmethod
    async def get_subcategory_by_id(self, subcategory_id: uuid.UUID) -> Optional[Subcategory]:
        """Get subcategory by ID."""
        ...

    @abstractmethod
    async def get_subcategories_by_category(
        self, category_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Subcategory]:
        """Get all active subcategories for a category."""
        ...

    @abstractmethod
    async def count_subcategories_by_category(self, category_id: uuid.UUID) -> int:
        """Count active subcategories for a category."""
        ...

    @abstractmethod
    async def update_subcategory(self, subcategory: Subcategory) -> Subcategory:
        """Update an existing subcategory."""
        ...

    @abstractmethod
    async def delete_subcategory(self, subcategory_id: uuid.UUID) -> bool:
        """Soft delete a subcategory."""
        ...