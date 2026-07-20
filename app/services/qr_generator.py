import io
import base64
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


def generate_qr_code_base64(data_url: str) -> str:
    """Generates a base64 Data-URI PNG image for the given URL/text."""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )
        qr.add_data(data_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.warning("Local qrcode module error (%s), using QR API fallback", e)
        encoded = quote(data_url)
        return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={encoded}"
