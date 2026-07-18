"""Equipment application service."""

import secrets
from typing import List, Optional
import uuid

from fastapi import HTTPException, status

from backend.app.application.dtos.equipment import (
    CreateEquipmentRequest,
    UpdateEquipmentRequest,
    EquipmentResponse,
    EquipmentListResponse,
)
from backend.app.domain.models.equipment import Equipment
from backend.app.domain.ports.equipment_repo import IEquipmentRepo
from backend.app.domain.ports.client_repo import IClientRepo
from backend.app.domain.ports.category_repo import ICategoryRepo


class EquipmentService:
    """Service layer for equipment CRUD operations."""

    def __init__(
        self,
        equipment_repo: IEquipmentRepo,
        client_repo: IClientRepo,
        category_repo: ICategoryRepo,
    ) -> None:
        self.equipment_repo = equipment_repo
        self.client_repo = client_repo
        self.category_repo = category_repo

    async def _resolve_names(self, equipment: Equipment) -> EquipmentResponse:
        """Resolve category and subcategory names for an equipment item.

        Args:
            equipment: The equipment model instance.

        Returns:
            EquipmentResponse with resolved names.
        """
        resp = EquipmentResponse.model_validate(equipment)

        # Resolve category name
        category = await self.category_repo.get_by_id(equipment.category_id)
        if category:
            resp.category_name = category.name

        # Resolve subcategory name if present
        if equipment.subcategory_id:
            subcategory = await self.category_repo.get_subcategory_by_id(
                equipment.subcategory_id
            )
            if subcategory:
                resp.subcategory_name = subcategory.name

        return resp

    async def _resolve_names_bulk(self, items: List[Equipment]) -> List[EquipmentResponse]:
        """Resolve names for a list of equipment items (batch optimization).

        Args:
            items: List of equipment model instances.

        Returns:
            List of EquipmentResponse with resolved names.
        """
        # Collect unique category and subcategory IDs
        cat_ids = set()
        subcat_ids = set()
        for eq in items:
            cat_ids.add(eq.category_id)
            if eq.subcategory_id:
                subcat_ids.add(eq.subcategory_id)

        # Batch-fetch categories and subcategories
        cat_map = {}
        for cid in cat_ids:
            cat = await self.category_repo.get_by_id(cid)
            if cat:
                cat_map[cid] = cat.name

        subcat_map = {}
        for sid in subcat_ids:
            subcat = await self.category_repo.get_subcategory_by_id(sid)
            if subcat:
                subcat_map[sid] = subcat.name

        # Build responses with resolved names
        results = []
        for eq in items:
            resp = EquipmentResponse.model_validate(eq)
            resp.category_name = cat_map.get(eq.category_id)
            if eq.subcategory_id:
                resp.subcategory_name = subcat_map.get(eq.subcategory_id)
            results.append(resp)

        return results

    async def create(self, request: CreateEquipmentRequest) -> EquipmentResponse:
        """Create new equipment with an auto-generated QR code.

        Args:
            request: Equipment creation data.

        Returns:
            Created equipment response.

        Raises:
            HTTPException 404: If referenced client or category not found.
            HTTPException 409: If serial number already exists.
        """
        # Validate client exists and is active
        client = await self.client_repo.get_by_id(request.client_id)
        if not client or not client.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        # Validate category exists
        category = await self.category_repo.get_by_id(request.category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        # Validate subcategory if provided
        if request.subcategory_id:
            subcategory = await self.category_repo.get_subcategory_by_id(
                request.subcategory_id
            )
            if not subcategory or not subcategory.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subcategory not found",
                )

        # Validate serial number uniqueness
        existing_serial = await self.equipment_repo.get_by_serial_number(
            request.serial_number
        )
        if existing_serial:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Equipment with serial number '{request.serial_number}' already exists",
            )

        # Generate unique QR code token
        qr_code = secrets.token_urlsafe(16)

        equipment = Equipment(
            client_id=request.client_id,
            category_id=request.category_id,
            subcategory_id=request.subcategory_id,
            brand=request.brand,
            model=request.model,
            serial_number=request.serial_number,
            qr_code=qr_code,
        )
        created = await self.equipment_repo.create(equipment)
        return await self._resolve_names(created)

    async def get_by_id(self, equipment_id: uuid.UUID) -> EquipmentResponse:
        """Get equipment by ID.

        Args:
            equipment_id: UUID of the equipment.

        Returns:
            Equipment response.

        Raises:
            HTTPException 404: If equipment not found or inactive.
        """
        equipment = await self.equipment_repo.get_by_id(equipment_id)
        if not equipment or not equipment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )
        return await self._resolve_names(equipment)

    async def get_by_qr(self, qr_code: str) -> EquipmentResponse:
        """Get equipment by QR code (public endpoint).

        Args:
            qr_code: The QR code token string.

        Returns:
            Equipment response.

        Raises:
            HTTPException 404: If no equipment matches the QR code.
        """
        equipment = await self.equipment_repo.get_by_qr(qr_code)
        if not equipment or not equipment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found for this QR code",
            )
        return await self._resolve_names(equipment)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        client_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
    ) -> EquipmentListResponse:
        """List active equipment with optional filters and pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            client_id: Optional filter by client UUID.
            category_id: Optional filter by category UUID.

        Returns:
            Paginated equipment list.
        """
        items = await self.equipment_repo.get_filtered(
            skip=skip,
            limit=limit,
            client_id=client_id,
            category_id=category_id,
        )
        total = await self.equipment_repo.count_filtered(
            client_id=client_id,
            category_id=category_id,
        )
        resolved = await self._resolve_names_bulk(items)
        return EquipmentListResponse(
            items=resolved,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update(
        self,
        equipment_id: uuid.UUID,
        request: UpdateEquipmentRequest,
    ) -> EquipmentResponse:
        """Update equipment (partial update).

        Args:
            equipment_id: UUID of the equipment to update.
            request: Fields to update (only non-None values applied).

        Returns:
            Updated equipment response.

        Raises:
            HTTPException 404: If equipment not found.
            HTTPException 409: If new serial number conflicts.
        """
        equipment = await self.equipment_repo.get_by_id(equipment_id)
        if not equipment or not equipment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )

        update_data = request.model_dump(exclude_unset=True)

        # Validate serial number uniqueness if changing
        if "serial_number" in update_data and update_data["serial_number"] != equipment.serial_number:
            existing = await self.equipment_repo.get_by_serial_number(
                update_data["serial_number"]
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Equipment with serial number '{update_data['serial_number']}' already exists",
                )

        # Validate client if changing
        if "client_id" in update_data:
            client = await self.client_repo.get_by_id(update_data["client_id"])
            if not client or not client.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client not found",
                )

        # Validate category if changing
        if "category_id" in update_data:
            category = await self.category_repo.get_by_id(update_data["category_id"])
            if not category or not category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found",
                )

        # Validate subcategory if changing
        if "subcategory_id" in update_data and update_data["subcategory_id"]:
            subcategory = await self.category_repo.get_subcategory_by_id(
                update_data["subcategory_id"]
            )
            if not subcategory or not subcategory.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subcategory not found",
                )

        for field, value in update_data.items():
            setattr(equipment, field, value)

        updated = await self.equipment_repo.update(equipment)
        return await self._resolve_names(updated)

    async def delete(self, equipment_id: uuid.UUID) -> None:
        """Soft-delete equipment.

        Args:
            equipment_id: UUID of the equipment to delete.

        Raises:
            HTTPException 404: If equipment not found.
        """
        equipment = await self.equipment_repo.get_by_id(equipment_id)
        if not equipment or not equipment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )

        await self.equipment_repo.delete(equipment_id)
