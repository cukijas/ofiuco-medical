"""OneDrive API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.onedrive.client import OneDriveClient
from backend.app.infrastructure.database.equipment_repo_impl import EquipmentRepo
from backend.app.domain.models.user import User

import uuid

router = APIRouter(prefix="/onedrive", tags=["onedrive"])


@router.post("/sync/{equipment_id}", status_code=status.HTTP_200_OK)
async def sync_equipment_folders(
    equipment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create OneDrive folder structure for an equipment.

    Creates the standard folder hierarchy:
    - 01_ORDENES_DE_SERVICIO
    - 02_INFORMES
    - 03_FOTOS_EQUIPO
    - 04_MANUALES

    Also updates the equipment's onedrive_path in the database.

    Args:
        equipment_id: UUID of the equipment.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Dict with folder IDs and base path.
    """
    # Validate equipment exists
    equipment_repo = EquipmentRepo(db)
    equipment = await equipment_repo.get_by_id(equipment_id)
    if not equipment or not equipment.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    onedrive = OneDriveClient(db)

    # Build equipment base path using serial number for uniqueness
    equipment_path = f"Equipment/{equipment.serial_number}"

    try:
        folder_ids = await onedrive.create_equipment_folders(equipment_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create OneDrive folders: {e}",
        )

    # Update equipment's onedrive_path
    equipment.onedrive_path = equipment_path
    await equipment_repo.update(equipment)

    return {
        "equipment_id": str(equipment_id),
        "onedrive_path": equipment_path,
        "folders": folder_ids,
    }


@router.get("/status")
async def onedrive_status(
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Check OneDrive connection status.

    Validates that the OAuth2 tokens are configured and the
    Microsoft Graph API is reachable.

    Args:
        current_user: Authenticated admin.
        db: Database session.

    Returns:
        Dict with connection status and user info.
    """
    onedrive = OneDriveClient(db)
    try:
        result = await onedrive.check_connection()
        return result
    except Exception as e:
        return {"connected": False, "error": str(e)}
