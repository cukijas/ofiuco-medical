"""Domain enums for the Ofiuco Medical service order system."""

import enum


class RoleEnum(str, enum.Enum):
    """User roles."""
    admin = "admin"
    technician = "technician"


class StatusEnum(str, enum.Enum):
    """Service order status."""
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"
    delivered = "delivered"


class CategoryEnum(str, enum.Enum):
    """Equipment categories."""
    rayos = "rayos"
    mamografos = "mamografos"
    arco_en_c = "arco_en_c"
    tomografos = "tomografos"


class AttachmentTypeEnum(str, enum.Enum):
    """Attachment types."""
    report = "report"
    photo = "photo"
    manual = "manual"
    other = "other"
