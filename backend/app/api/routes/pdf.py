"""PDF generation API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.auth.dependencies import require_role
from backend.app.infrastructure.pdf.generator import PdfGenerator
from backend.app.infrastructure.database.service_order_repo_impl import ServiceOrderRepo
from backend.app.domain.models.user import User

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.get("/orders/{order_id}")
async def download_order_pdf(
    order_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download PDF for a service order.

    Generates a PDF document from the order data, including client
    info, equipment info, parts, and technician details.

    Args:
        order_id: UUID of the service order.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        PDF file as HTTP response with appropriate content type.
    """
    # Validate order exists
    order_repo = ServiceOrderRepo(db)
    order = await order_repo.get_by_id(order_id)
    if not order or not order.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    generator = PdfGenerator(db)
    try:
        pdf_bytes = await generator.generate_order_pdf(order_id)
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

    filename = f"{order.order_number}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("/orders/{order_id}/regenerate")
async def regenerate_order_pdf(
    order_id: uuid.UUID,
    current_user: User = Depends(require_role(["admin", "technician"])),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Regenerate PDF for a service order.

    Same as download but returns metadata instead of the file.
    Useful for triggering regeneration and confirming success.

    Args:
        order_id: UUID of the service order.
        current_user: Authenticated admin or technician.
        db: Database session.

    Returns:
        Dict with order number and PDF size.
    """
    # Validate order exists
    order_repo = ServiceOrderRepo(db)
    order = await order_repo.get_by_id(order_id)
    if not order or not order.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    generator = PdfGenerator(db)
    try:
        pdf_bytes = await generator.generate_order_pdf(order_id)
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

    return {
        "order_number": order.order_number,
        "pdf_size_bytes": len(pdf_bytes),
        "status": "regenerated",
    }
