"""PDF generation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.pdf.generator import PdfGenerator
from backend.app.domain.models.ordenes_servicio import OrdenesServicio
from backend.app.domain.models.user import User

router = APIRouter(prefix="/ordenes-servicio", tags=["pdf"])


@router.get("/{orden_id}/pdf")
async def download_order_pdf(
    orden_id: int,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download PDF for a service order.

    Generates a PDF document from the order data, including client
    info, equipment info, parts, and technician details.

    Args:
        orden_id: Integer ID of the service order.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        PDF file as HTTP response with appropriate content type.
    """
    # Validate order exists
    result = await db.execute(
        select(OrdenesServicio).where(OrdenesServicio.id_orden == orden_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    generator = PdfGenerator(db)
    try:
        pdf_bytes = await generator.generate_order_pdf(orden_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    filename = f"{order.numero_orden}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
