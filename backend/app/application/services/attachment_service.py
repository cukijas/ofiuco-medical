"""Attachment application service."""

import logging
from typing import Optional
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.dtos.attachment import AttachmentResponse, AttachmentListResponse
from backend.app.domain.enums import AttachmentTypeEnum
from backend.app.domain.models.attachment import Attachment
from backend.app.domain.ports.attachment_repo import IAttachmentRepo
from backend.app.domain.ports.onedrive_client import IOneDriveClient

logger = logging.getLogger(__name__)

# 50MB file size limit
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed MIME types mapped to AttachmentTypeEnum
ALLOWED_TYPES: dict[str, AttachmentTypeEnum] = {
    "application/pdf": AttachmentTypeEnum.report,
    "image/jpeg": AttachmentTypeEnum.photo,
    "image/png": AttachmentTypeEnum.photo,
    "image/heic": AttachmentTypeEnum.photo,
    "image/webp": AttachmentTypeEnum.photo,
    "text/plain": AttachmentTypeEnum.manual,
    "application/msword": AttachmentTypeEnum.manual,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": AttachmentTypeEnum.manual,
}


class AttachmentService:
    """Service layer for attachment operations."""

    def __init__(
        self,
        attachment_repo: IAttachmentRepo,
        onedrive_client: IOneDriveClient,
        session: AsyncSession,
    ) -> None:
        self.attachment_repo = attachment_repo
        self.onedrive = onedrive_client
        self.session = session

    async def upload(
        self,
        file: UploadFile,
        uploaded_by: uuid.UUID,
        equipment_id: Optional[uuid.UUID] = None,
        service_order_id: Optional[uuid.UUID] = None,
        file_type: Optional[str] = None,
    ) -> AttachmentResponse:
        """Upload a file attachment.

        Validates file type and size, uploads to OneDrive, and persists
        the attachment metadata.

        Args:
            file: The uploaded file from FastAPI.
            uploaded_by: UUID of the uploading user.
            equipment_id: Optional equipment to associate with.
            service_order_id: Optional service order to associate with.
            file_type: Optional explicit file type override.

        Returns:
            Created attachment response.

        Raises:
            HTTPException 400: If file type is not allowed.
            HTTPException 413: If file exceeds size limit.
            HTTPException 502: If OneDrive upload fails.
        """
        # Validate file type
        content_type = file.content_type or "application/octet-stream"
        if file_type:
            try:
                attachment_type = AttachmentTypeEnum(file_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type '{file_type}'. Valid: {[t.value for t in AttachmentTypeEnum]}",
                )
        else:
            attachment_type = ALLOWED_TYPES.get(content_type)
            if attachment_type is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type '{content_type}' not allowed. Allowed: {list(ALLOWED_TYPES.keys())}",
                )

        # Read file content and validate size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        # Determine OneDrive path
        onedrive_path = await self._get_upload_path(
            attachment_type, equipment_id, service_order_id
        )

        # Upload to OneDrive
        try:
            item_id = await self.onedrive.upload_file(
                folder_path=onedrive_path,
                file_name=file.filename or "unnamed",
                file_content=content,
            )
        except Exception as e:
            logger.error("OneDrive upload failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"File storage upload failed: {e}",
            )

        # Persist metadata
        attachment = Attachment(
            service_order_id=service_order_id,
            equipment_id=equipment_id,
            file_name=file.filename or "unnamed",
            file_type=attachment_type,
            onedrive_path=f"{onedrive_path}/{file.filename}",
            uploaded_by=uploaded_by,
            is_active=True,
        )
        created = await self.attachment_repo.create(attachment)
        logger.info(
            "Attachment uploaded: %s (id=%s) by user %s",
            file.filename, created.id, uploaded_by,
        )
        return AttachmentResponse.model_validate(created)

    async def list_by_equipment(
        self, equipment_id: uuid.UUID
    ) -> AttachmentListResponse:
        """List active attachments for an equipment.

        Args:
            equipment_id: UUID of the equipment.

        Returns:
            List of attachments.
        """
        items = await self.attachment_repo.get_by_equipment(equipment_id)
        active = [a for a in items if a.is_active]
        return AttachmentListResponse(
            items=[AttachmentResponse.model_validate(a) for a in active],
            total=len(active),
        )

    async def list_by_order(
        self, order_id: uuid.UUID
    ) -> AttachmentListResponse:
        """List active attachments for a service order.

        Args:
            order_id: UUID of the service order.

        Returns:
            List of attachments.
        """
        items = await self.attachment_repo.get_by_order(order_id)
        active = [a for a in items if a.is_active]
        return AttachmentListResponse(
            items=[AttachmentResponse.model_validate(a) for a in active],
            total=len(active),
        )

    async def download(
        self, attachment_id: uuid.UUID
    ) -> tuple[str, bytes]:
        """Download an attachment file from OneDrive.

        Args:
            attachment_id: UUID of the attachment.

        Returns:
            Tuple of (file_name, file_content_bytes).

        Raises:
            HTTPException 404: If attachment not found.
            HTTPException 502: If OneDrive download fails.
        """
        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment or not attachment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )

        if not attachment.onedrive_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment file not available in storage",
            )

        try:
            download_url = await self.onedrive.get_item_download_url(
                attachment.onedrive_path
            )
            if not download_url:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found in OneDrive",
                )

            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(download_url)
                response.raise_for_status()
                return attachment.file_name, response.content

        except HTTPException:
            raise
        except Exception as e:
            logger.error("OneDrive download failed for attachment %s: %s", attachment_id, e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"File download failed: {e}",
            )

    async def delete(
        self,
        attachment_id: uuid.UUID,
        remove_from_onedrive: bool = False,
    ) -> bool:
        """Soft-delete an attachment.

        Args:
            attachment_id: UUID of the attachment to delete.
            remove_from_onedrive: If True, also delete the file from OneDrive.

        Returns:
            True if deleted.

        Raises:
            HTTPException 404: If attachment not found.
        """
        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment or not attachment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )

        # Optionally remove from OneDrive
        if remove_from_onedrive and attachment.onedrive_path:
            try:
                await self.onedrive.delete_item(attachment.onedrive_path)
            except Exception as e:
                logger.warning(
                    "Failed to delete OneDrive file for attachment %s: %s",
                    attachment_id, e,
                )

        # Soft delete
        attachment.is_active = False
        await self.attachment_repo.update(attachment)
        logger.info("Soft-deleted attachment %s", attachment_id)
        return True

    async def _get_upload_path(
        self,
        file_type: AttachmentTypeEnum,
        equipment_id: Optional[uuid.UUID],
        service_order_id: Optional[uuid.UUID],
    ) -> str:
        """Determine the OneDrive upload path based on context.

        Args:
            file_type: Type of attachment.
            equipment_id: Optional equipment UUID.
            service_order_id: Optional service order UUID.

        Returns:
            OneDrive folder path string.
        """
        if file_type == AttachmentTypeEnum.photo:
            return "03_FOTOS_EQUIPO"
        elif file_type == AttachmentTypeEnum.manual:
            return "04_MANUALES"
        elif file_type == AttachmentTypeEnum.report:
            return "02_INFORMES"
        else:
            return "02_INFORMES"
