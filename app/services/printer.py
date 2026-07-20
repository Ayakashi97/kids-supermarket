import logging
from app.config import Config

logger = logging.getLogger(__name__)


def print_receipt(transaction_data: dict) -> bool:
    """Print thermal receipt using python-escpos. Gracefully fallback if hardware not available."""
    try:
        from escpos.printer import File

        device_path = Config.PRINTER_DEVICE
        logger.info("Attempting to print receipt on device %s...", device_path)

        # Basic fallback log if device file doesn't exist
        # Real ESC/POS printing will be fully wired up in Phase 4
        logger.info("Receipt mock print for Transaction #%s: %s",
                    transaction_data.get("id"), transaction_data)
        return True
    except Exception as e:
        logger.warning("Thermal printer not available or printing failed: %s", str(e))
        return False
