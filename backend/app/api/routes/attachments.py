"""Attachment API routes."""

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.attachment import AttachmentResponse, AttachmentListResponse
from backend.app.application.services.attachment_service import AttachmentService
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.database.attachment_repo_impl import AttachmentRepo
from backend.app.infrastructure.onedrive.client import OneDriveClient
from backend.app.domain.models.user import User

router = APIRouter(prefix="/attachments", tags=["attachments"])


def _build_service(db: AsyncSession) -> AttachmentService:
    """Create AttachmentService with its dependencies."""
    attachment_repo = AttachmentRepo(db)
    onedrive_client = OneDriveClient(db)
    return AttachmentService(attachment_repo, onedrive_client, db)


@router.post(
    "/upload",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    file: UploadFile = File(..., description="File to upload"),
    equipment_id: uuid.UUID | None = Form(None, description="Related equipment UUID"),
    service_order_id: uuid.UUID | None = Form(None, description="Related service order UUID"),
    file_type: str | None = Form(None, description="File type override (report, photo, manual, other)"),
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> AttachmentResponse:
    """Upload a file attachment.

    Accepts multipart form data with the file and optional metadata.
    File is validated (type, 50MB size limit), uploaded to OneDrive,
    and metadata is saved to the database.

    Args:
        file: The file to upload.
        equipment_id: Optional equipment to associate with.
        service_order_id: Optional service order to associate with.
        file_type: Optional explicit file type.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Created attachment data.
    """
    service = _build_service(db)
    return await service.upload(
        file=file,
        uploaded_by=current_user.id,
        equipment_id=equipment_id,
        service_order_id=service_order_id,
        file_type=file_type,
    )


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download an attachment file.

    Fetches the file from OneDrive and returns it as a binary response.

    Args:
        attachment_id: UUID of the attachment.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        File content as HTTP response.
    """
    service = _build_service(db)
    file_name, content = await service.download(attachment_id)

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
        },
    )


@router.get("/equipment/{equipment_id}", response_model=AttachmentListResponse)
async def list_attachments_by_equipment(
    equipment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> AttachmentListResponse:
    """List attachments for an equipment.

    Args:
        equipment_id: UUID of the equipment.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        List of attachments.
    """
    service = _build_service(db)
    return await service.list_by_equipment(equipment_id)


@router.get("/orders/{order_id}", response_model=AttachmentListResponse)
async def list_attachments_by_order(
    order_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> AttachmentListResponse:
    """List attachments for a service order.

    Args:
        order_id: UUID of the service order.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        List of attachments.
    """
    service = _build_service(db)
    return await service.list_by_order(order_id)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an attachment (admin only).

    Marks the attachment as inactive. Does not remove the file
    from OneDrive storage by default.

    Args:
        attachment_id: UUID of the attachment to delete.
        current_user: Authenticated admin.
        db: Database session.
    """
    service = _build_service(db)
    await service.delete(attachment_id)
    return None
