"""Domain enums for the Ofiuco Medical service order system."""

import enum


# ── Existing enums (still used by auth, users, orders) ──

class RoleEnum(str, enum.Enum):
    admin = "admin"
    technician = "technician"


class StatusEnum(str, enum.Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"
    delivered = "delivered"


class VisitTypeEnum(str, enum.Enum):
    normal = "normal"
    contract = "contract"
    warranty = "warranty"


class EquipmentConditionEnum(str, enum.Enum):
    new = "new"
    used = "used"
    other = "other"


class AttachmentTypeEnum(str, enum.Enum):
    report = "report"
    photo = "photo"
    manual = "manual"
    other = "other"


# ── New enums (from redesigned schema) ──

class TipoClienteEnum(str, enum.Enum):
    """Tipo de cliente."""
    fisica = "fisica"
    juridica = "juridica"


class CondicionEnum(str, enum.Enum):
    """Condición de equipo."""
    nuevo = "nuevo"
    usado = "usado"
    otro = "otro"


class TipoVisitaEnum(str, enum.Enum):
    """Tipo de visita de servicio."""
    normal = "normal"
    por_contrato = "por contrato"
    por_garantia = "por garantia"
