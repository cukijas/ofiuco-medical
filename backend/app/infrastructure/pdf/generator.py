"""PDF generator adapter — WeasyPrint HTML to PDF conversion."""

import base64
import logging
from pathlib import Path

import jinja2
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.departamentos import Departamentos
from backend.app.domain.models.empleados import Empleados
from backend.app.domain.models.equipos import Equipos
from backend.app.domain.models.insumos import Insumos
from backend.app.domain.models.marcas import Marcas
from backend.app.domain.models.ordenes_servicio import OrdenesServicio
from backend.app.domain.models.tipo_equipos import TipoEquipos
from backend.app.domain.ports.pdf_generator import IPdfGenerator

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"

# Logo path (project root relative)
LOGO_PATH = (
    Path(__file__).parent.parent.parent.parent.parent
    / "os_modelo"
    / "WhatsApp Image 2026-07-18 at 17.12.06.jpeg"
)


class PdfGenerator(IPdfGenerator):
    """WeasyPrint-based PDF generator for service orders."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=False,
        )

    async def generate_order_pdf(self, order_id: int) -> bytes:
        """Generate a PDF for a service order.

        Fetches all related entities (order, client, equipment, technician,
        additional technicians, insumos), renders the HTML template with
        embedded logo and QR code, then converts to PDF via WeasyPrint.

        Args:
            order_id: Integer ID of the service order.

        Returns:
            PDF file as bytes.

        Raises:
            ValueError: If order or required related entities not found.
        """
        # Fetch the order
        result = await self.session.execute(
            select(OrdenesServicio).where(OrdenesServicio.id_orden == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError(f"Service order {order_id} not found")

        # Fetch client
        client = await self._fetch_by_id(Clientes, Clientes.id_cliente, order.id_cliente)
        if not client:
            raise ValueError(f"Client {order.id_cliente} not found for order {order_id}")

        # Fetch equipment
        equipo = await self._fetch_by_id(Equipos, Equipos.id_equipos, order.id_equipo)
        if not equipo:
            raise ValueError(f"Equipment {order.id_equipo} not found for order {order_id}")

        # Fetch primary technician
        empleado = await self._fetch_by_id(
            Empleados, Empleados.id_empleado, order.id_empleado
        )
        if not empleado:
            raise ValueError(
                f"Employee {order.id_empleado} not found for order {order_id}"
            )

        # Fetch equipment category (TipoEquipos)
        tipo_equipo = await self._fetch_by_id(
            TipoEquipos, TipoEquipos.id_tipo_equipos, equipo.id_tipo_equipos
        )

        # Fetch equipment brand (Marcas)
        marca = await self._fetch_by_id(Marcas, Marcas.id_marca, equipo.id_marca)

        # Fetch department (nullable)
        departamento = None
        if order.id_departamento:
            departamento = await self._fetch_by_id(
                Departamentos,
                Departamentos.id_departamento,
                order.id_departamento,
            )

        # Resolve additional technician IDs to names
        tecnicos_adicionales = await self._resolve_additional_techs(
            order.empleados_adicionales
        )

        # Fetch insumos for this order
        insumos_result = await self.session.execute(
            select(Insumos).where(Insumos.id_orden == order_id)
        )
        insumos = list(insumos_result.scalars().all())

        # Embed logo as base64
        logo_base64 = self._load_logo_base64()

        # Generate QR code as base64 (using equipment's qr_identifier)
        qr_base64 = ""
        if equipo.qr_identifier:
            qr_base64 = self._generate_qr_base64(
                f"https://ofiuco.com/equipment/{equipo.qr_identifier}"
            )

        # Build template context
        context = {
            "order": order,
            "client": client,
            "equipo": equipo,
            "empleado": empleado,
            "marca": marca,
            "tipo_equipo": tipo_equipo,
            "departamento": departamento,
            "tecnicos_adicionales": tecnicos_adicionales,
            "insumos": insumos,
            "logo_base64": logo_base64,
            "qr_base64": qr_base64,
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
                order.numero_orden,
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
            logger.error(
                "PDF generation failed for order %s: %s", order.numero_orden, e
            )
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

    async def _resolve_additional_techs(
        self, empleados_adicionales: str | None
    ) -> list[Empleados]:
        """Resolve comma-separated employee IDs to Empleados objects.

        Unknown IDs are represented as lightweight fallback objects with
        a ``nombre`` attribute set to the raw ID string.

        Args:
            empleados_adicionales: Comma-separated employee IDs, or None.

        Returns:
            List of Empleados instances (or fallback objects).
        """
        if not empleados_adicionales or not empleados_adicionales.strip():
            return []

        raw_ids = [
            int(tid.strip())
            for tid in empleados_adicionales.split(",")
            if tid.strip()
        ]
        if not raw_ids:
            return []

        result = await self.session.execute(
            select(Empleados).where(Empleados.id_empleado.in_(raw_ids))
        )
        found = {e.id_empleado: e for e in result.scalars().all()}

        # Preserve order from the comma-separated string; fallback for missing IDs
        techs = []
        for tid in raw_ids:
            if tid in found:
                techs.append(found[tid])
            else:
                # Lightweight fallback — has .nombre attribute for template rendering
                fallback = type("FallbackTech", (), {"nombre": str(tid)})()
                techs.append(fallback)

        return techs

    async def _fetch_by_id(self, model_class, pk_column, entity_id):
        """Fetch a single entity by its primary key column.

        Args:
            model_class: SQLAlchemy model class.
            pk_column: The primary key column of the model.
            entity_id: ID value to match.

        Returns:
            The entity instance, or None if not found.
        """
        result = await self.session.execute(
            select(model_class).where(pk_column == entity_id)
        )
        return result.scalar_one_or_none()
