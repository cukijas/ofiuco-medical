"""Domain ports package."""

from backend.app.domain.ports.user_repo import IUserRepo
from backend.app.domain.ports.client_repo import IClientRepo
from backend.app.domain.ports.equipment_repo import IEquipmentRepo
from backend.app.domain.ports.service_order_repo import IServiceOrderRepo
from backend.app.domain.ports.attachment_repo import IAttachmentRepo
from backend.app.domain.ports.onedrive_client import IOneDriveClient
from backend.app.domain.ports.pdf_generator import IPdfGenerator

__all__ = [
    "IUserRepo",
    "IClientRepo",
    "IEquipmentRepo",
    "IServiceOrderRepo",
    "IAttachmentRepo",
    "IOneDriveClient",
    "IPdfGenerator",
]
