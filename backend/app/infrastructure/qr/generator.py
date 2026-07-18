"""QR code image generator adapter."""

import io

import qrcode
from qrcode.image.pil import PilImage


def generate_qr_png(url: str, box_size: int = 10, border: int = 4) -> bytes:
    """Generate a QR code PNG image for the given URL.

    Args:
        url: The URL to encode in the QR code.
        box_size: Pixel size of each QR box (default 10).
        border: Border thickness in boxes (default 4).

    Returns:
        PNG image as raw bytes.
    """
    qr = qrcode.QRCode(
        version=None,  # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
