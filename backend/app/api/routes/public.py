"""Public routes — no authentication required."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.attachment import Attachment
from backend.app.domain.models.equipment import Equipment
from backend.app.domain.models.service_order import ServiceOrder
from backend.app.domain.models.client import Client
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.onedrive.client import OneDriveClient

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/equipment/{qr_id}", response_class=HTMLResponse)
async def public_equipment_info(
    qr_id: str,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Public equipment information page — no auth required.

    Renders a mobile-responsive HTML page showing equipment details
    and service order history. Accessed via QR code scanning.

    Args:
        qr_id: QR code token from equipment.
        db: Database session.

    Returns:
        HTML page with equipment info and service history.

    Raises:
        HTML 404: If no equipment matches the QR code.
    """
    # Find equipment by QR code
    result = await db.execute(
        select(Equipment).where(Equipment.qr_code == qr_id, Equipment.is_active == True)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        return HTMLResponse(
            content=_render_not_found(qr_id),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Fetch client
    client_result = await db.execute(
        select(Client).where(Client.id == equipment.client_id)
    )
    client = client_result.scalar_one_or_none()

    # Fetch service orders
    orders_result = await db.execute(
        select(ServiceOrder)
        .where(ServiceOrder.equipment_id == equipment.id, ServiceOrder.is_active == True)
        .order_by(ServiceOrder.created_at.desc())
        .limit(20)
    )
    orders = list(orders_result.scalars().all())

    # Fetch attachments for this equipment
    attachments_result = await db.execute(
        select(Attachment)
        .where(Attachment.equipment_id == equipment.id, Attachment.is_active == True)
        .order_by(Attachment.created_at.desc())
    )
    attachments = list(attachments_result.scalars().all())

    html = _render_equipment_page(equipment, client, orders, attachments)
    return HTMLResponse(content=html)


@router.get("/equipment/{qr_id}/attachments/{attachment_id}")
async def public_download_attachment(
    qr_id: str,
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download an attachment via public link — no auth required.

    Validates that the attachment belongs to equipment matching the QR code
    before allowing download.

    Args:
        qr_id: QR code token from equipment.
        attachment_id: UUID of the attachment to download.
        db: Database session.

    Returns:
        File content as HTTP response.

    Raises:
        HTML 404: If equipment or attachment not found.
    """
    # Validate equipment
    eq_result = await db.execute(
        select(Equipment).where(Equipment.qr_code == qr_id, Equipment.is_active == True)
    )
    equipment = eq_result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Validate attachment belongs to this equipment
    att_result = await db.execute(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.equipment_id == equipment.id,
            Attachment.is_active == True,
        )
    )
    attachment = att_result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    if not attachment.onedrive_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not available",
        )

    # Download from OneDrive
    try:
        onedrive = OneDriveClient(db)
        download_url = await onedrive.get_item_download_url(attachment.onedrive_path)
        if not download_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in storage",
            )

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{attachment.file_name}"',
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=f"Download failed: {e}",
        )


def _render_equipment_page(
    equipment: Equipment,
    client: Client | None,
    orders: list[ServiceOrder],
    attachments: list[Attachment],
) -> str:
    """Render the public equipment information HTML page.

    Args:
        equipment: Equipment entity.
        client: Client entity (optional).
        orders: List of service orders.
        attachments: List of attachments.

    Returns:
        Complete HTML string.
    """
    orders_html = ""
    for order in orders:
        status_class = f"status-{order.status}"
        status_display = order.status.replace("_", " ").title()
        service_date = order.service_date.strftime("%d/%m/%Y") if order.service_date else "Sin fecha"
        orders_html += f"""
        <div class="order-card">
            <div class="order-header">
                <span class="order-number">{order.order_number}</span>
                <span class="status-badge {status_class}">{status_display}</span>
            </div>
            <div class="order-date">Fecha: {service_date}</div>
            {f'<div class="order-desc">{order.description}</div>' if order.description else ''}
        </div>
        """

    if not orders:
        orders_html = '<p class="empty">No hay órdenes de servicio registradas.</p>'

    attachments_html = ""
    for att in attachments:
        attachments_html += f"""
        <div class="attachment-item">
            <span class="att-icon">&#128206;</span>
            <span class="att-name">{att.file_name}</span>
            <span class="att-type">{att.file_type}</span>
        </div>
        """

    if not attachments:
        attachments_html = '<p class="empty">No hay archivos adjuntos.</p>'

    client_name = client.name if client else "—"
    client_phone = client.phone if client and client.phone else "—"
    client_city = ""
    if client:
        if client.city:
            client_city = client.city
            if client.province:
                client_city += f", {client.province}"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equipo {equipment.brand} {equipment.model}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.5;
            padding: 16px;
        }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{
            background: #1a5276;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h1 {{ font-size: 18px; margin-bottom: 4px; }}
        .header .subtitle {{ font-size: 12px; opacity: 0.8; }}
        .card {{
            background: white;
            padding: 16px;
            border-bottom: 1px solid #eee;
        }}
        .card:last-child {{ border-radius: 0 0 8px 8px; border-bottom: none; }}
        .card h2 {{
            font-size: 13px;
            color: #1a5276;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            padding-bottom: 6px;
            border-bottom: 2px solid #1a5276;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 14px;
        }}
        .info-label {{ color: #666; }}
        .info-value {{ font-weight: 600; }}
        .order-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
        }}
        .order-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }}
        .order-number {{ font-weight: 700; font-size: 15px; }}
        .order-date {{ font-size: 12px; color: #666; }}
        .order-desc {{ font-size: 13px; color: #555; margin-top: 4px; }}
        .status-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .status-draft {{ background: #f0f0f0; color: #666; }}
        .status-in_progress {{ background: #fef3cd; color: #856404; }}
        .status-completed {{ background: #d4edda; color: #155724; }}
        .status-delivered {{ background: #cce5ff; color: #004085; }}
        .attachment-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            margin-bottom: 6px;
            font-size: 13px;
        }}
        .att-icon {{ font-size: 18px; }}
        .att-name {{ flex: 1; font-weight: 500; }}
        .att-type {{ font-size: 11px; color: #999; text-transform: uppercase; }}
        .empty {{ font-style: italic; color: #999; font-size: 13px; }}
        .footer {{
            text-align: center;
            font-size: 11px;
            color: #999;
            margin-top: 16px;
            padding: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ofiuco Medical</h1>
            <div class="subtitle">Información del Equipo</div>
        </div>

        <div class="card">
            <h2>Equipo</h2>
            <div class="info-row">
                <span class="info-label">Marca</span>
                <span class="info-value">{equipment.brand}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Modelo</span>
                <span class="info-value">{equipment.model}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Serial</span>
                <span class="info-value">{equipment.serial_number}</span>
            </div>
        </div>

        <div class="card">
            <h2>Cliente</h2>
            <div class="info-row">
                <span class="info-label">Nombre</span>
                <span class="info-value">{client_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Teléfono</span>
                <span class="info-value">{client_phone}</span>
            </div>
            {f'<div class="info-row"><span class="info-label">Ciudad</span><span class="info-value">{client_city}</span></div>' if client_city else ''}
        </div>

        <div class="card">
            <h2>Órdenes de Servicio</h2>
            {orders_html}
        </div>

        <div class="card">
            <h2>Archivos Adjuntos</h2>
            {attachments_html}
        </div>

        <div class="footer">
            Ofiuco Medical &mdash; Servicio Técnico de Equipos Biomédicos
        </div>
    </div>
</body>
</html>"""


def _render_not_found(qr_id: str) -> str:
    """Render a 404 page for unknown QR codes.

    Args:
        qr_id: The QR code that was not found.

    Returns:
        HTML string for the 404 page.
    """
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equipo no encontrado</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 16px;
        }}
        .container {{
            text-align: center;
            background: white;
            padding: 40px 32px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            max-width: 400px;
        }}
        .icon {{ font-size: 48px; margin-bottom: 16px; }}
        h1 {{ font-size: 20px; color: #333; margin-bottom: 8px; }}
        p {{ color: #666; font-size: 14px; margin-bottom: 16px; }}
        .qr-id {{ font-family: monospace; font-size: 12px; color: #999; word-break: break-all; }}
        .footer {{ font-size: 11px; color: #ccc; margin-top: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">&#9888;</div>
        <h1>Equipo no encontrado</h1>
        <p>El código QR escaneado no corresponde a ningún equipo registrado en el sistema.</p>
        <div class="qr-id">QR: {qr_id}</div>
        <div class="footer">Ofiuco Medical</div>
    </div>
</body>
</html>"""
