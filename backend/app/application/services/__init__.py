"""Application services package."""

from backend.app.application.services.auth_service import AuthService

# Legacy services (pre-003 schema) — replaced by direct ORM routes (clientes, equipos, ordenes_servicio)
# from backend.app.application.services.client_service import ClientService
# from backend.app.application.services.equipment_service import EquipmentService
# from backend.app.application.services.order_service import OrderService
# from backend.app.application.services.attachment_service import AttachmentService

__all__ = [
    "AuthService",
]
