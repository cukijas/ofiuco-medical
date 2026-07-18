"""PDF generator adapter — WeasyPrint HTML to PDF conversion."""

import base64
import logging
import uuid
from pathlib import Path

import jinja2
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.attachment import Attachment
from backend.app.domain.models.category import Category
from backend.app.domain.models.client import Client
from backend.app.domain.models.equipment import Equipment
from backend.app.domain.models.service_order import ServiceOrder
from backend.app.domain.models.service_order_part import ServiceOrderPart
from backend.app.domain.models.user import User
from backend.app.domain.ports.pdf_generator import IPdfGenerator

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"

# Logo path (project root relative)
LOGO_PATH = Path(__file__).parent.parent.parent.parent.parent / "os_modelo" / "WhatsApp Image 2026-07-18 at 17.12.06.jpeg"


class PdfGenerator(IPdfGenerator):
    """WeasyPrint-based PDF generator for service orders."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=False,
        )

    async def generate_order_pdf(self, order_id: uuid.UUID) -> bytes:
        """Generate a PDF for a service order.

        Fetches all related entities (order, client, equipment, technician,
        parts), renders the HTML template with embedded logo and QR code,
        then converts to PDF via WeasyPrint.

        Args:
            order_id: UUID of the service order.

        Returns:
            PDF file as bytes.

        Raises:
            ValueError: If order or related entities not found.
        """
        # Fetch the order
        result = await self.session.execute(
            select(ServiceOrder).where(ServiceOrder.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError(f"Service order {order_id} not found")

        # Fetch related entities
        client = await self._get_entity(Client, order.client_id)
        equipment = await self._get_entity(Equipment, order.equipment_id)
        technician = await self._get_entity(User, order.technician_id)

        # Fetch equipment category name
        category_name = ""
        if equipment:
            category = await self._get_entity(Category, equipment.category_id)
            if category:
                category_name = category.name

        # Fetch parts
        parts_result = await self.session.execute(
            select(ServiceOrderPart).where(
                ServiceOrderPart.service_order_id == order_id,
                ServiceOrderPart.is_active == True,
            )
        )
        parts = list(parts_result.scalars().all())

        # Fetch attachments for this order
        attachments_result = await self.session.execute(
            select(Attachment).where(
                Attachment.service_order_id == order_id,
                Attachment.is_active == True,
            )
        )
        attachments = list(attachments_result.scalars().all())

        # Embed logo as base64
        logo_base64 = self._load_logo_base64()

        # Generate QR code as base64
        qr_base64 = ""
        if equipment and equipment.qr_code:
            qr_base64 = self._generate_qr_base64(
                f"https://ofiuco.com/equipment/{equipment.qr_code}"
            )

        # Build template context
        context = {
            "order": order,
            "client": client,
            "equipment": equipment,
            "technician": technician,
            "parts": parts,
            "attachments": attachments,
            "category_name": category_name,
            "logo_base64": logo_base64,
            "qr_base64": qr_base64,
            "status_display": order.status.replace("_", " ").title(),
        }

        # Render HTML
        template = self._env.get_template("service_order.html")
        html_content = template.render(**context)

        # Convert to PDF using WeasyPrint
        try:
            from weasyprint import HTML

            pdf_bytes = HTML(string=html_content).write_pdf()
            logger.info(
                "Generated PDF for order %s (%d bytes)",
                order.order_number,
                len(pdf_bytes),
            )
            return pdf_bytes
        except ImportError:
            logger.error("WeasyPrint not installed — cannot generate PDF")
            raise RuntimeError(
                "PDF generation unavailable: WeasyPrint is not installed. "
                "Install it with: pip install weasyprint"
            )
        except Exception as e:
            logger.error("PDF generation failed for order %s: %s", order.order_number, e)
            raise RuntimeError(f"PDF generation failed: {e}")

    def _load_logo_base64(self) -> str:
        """Load logo JPEG and return base64-encoded string.

        Returns:
            Base64-encoded logo, or empty string if file not found.
        """
        if not LOGO_PATH.exists():
            logger.warning("Logo file not found at %s", LOGO_PATH)
            return ""
        try:
            logo_bytes = LOGO_PATH.read_bytes()
            return base64.b64encode(logo_bytes).decode("ascii")
        except Exception as e:
            logger.error("Failed to load logo: %s", e)
            return ""

    def _generate_qr_base64(self, url: str) -> str:
        """Generate QR code PNG and return base64-encoded string.

        Args:
            url: URL to encode in the QR code.

        Returns:
            Base64-encoded QR PNG, or empty string on failure.
        """
        try:
            from backend.app.infrastructure.qr.generator import generate_qr_png

            qr_png = generate_qr_png(url)
            return base64.b64encode(qr_png).decode("ascii")
        except Exception as e:
            logger.error("Failed to generate QR code for %s: %s", url, e)
            return ""

    async def _get_entity(self, model_class, entity_id: uuid.UUID):
        """Fetch a single entity by ID.

        Args:
            model_class: SQLAlchemy model class.
            entity_id: UUID of the entity.

        Returns:
            The entity instance, or None if not found.
        """
        result = await self.session.execute(
            select(model_class).where(model_class.id == entity_id)
        )
        return result.scalar_one_or_none()
