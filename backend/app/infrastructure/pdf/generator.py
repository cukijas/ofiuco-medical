"""PDF generator adapter — WeasyPrint HTML to PDF conversion."""

import logging
import uuid
from pathlib import Path
from typing import Optional

import jinja2
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.attachment import Attachment
from backend.app.domain.models.client import Client
from backend.app.domain.models.equipment import Equipment
from backend.app.domain.models.service_order import ServiceOrder
from backend.app.domain.models.service_order_part import ServiceOrderPart
from backend.app.domain.models.user import User
from backend.app.domain.ports.pdf_generator import IPdfGenerator

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"


class PdfGenerator(IPdfGenerator):
    """WeasyPrint-based PDF generator for service orders."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=True,
        )

    async def generate_order_pdf(self, order_id: uuid.UUID) -> bytes:
        """Generate a PDF for a service order.

        Fetches all related entities (order, client, equipment, technician,
        parts), renders the HTML template, then converts to PDF via WeasyPrint.

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

        # Build template context
        context = {
            "order": order,
            "client": client,
            "equipment": equipment,
            "technician": technician,
            "parts": parts,
            "attachments": attachments,
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
