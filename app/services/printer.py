import os
import logging
from datetime import datetime
from app.config import Config
from app.models import Setting

logger = logging.getLogger(__name__)


def get_setting(key: str, default_val: str) -> str:
    """Helper to fetch a setting value from DB, with fallback to default."""
    try:
        setting = Setting.query.get(key)
        if setting and setting.value is not None:
            return setting.value
    except Exception as e:
        logger.debug("Could not read setting %s from DB: %s", key, e)
    return default_val


def print_receipt(transaction_data: dict) -> bool:
    """
    Prints a thermal receipt via python-escpos USB/File device.
    Configuration is dynamically read from DB settings with fallback to environment variables.
    """
    # Check if printer is enabled in settings
    printer_enabled_str = get_setting("printer_enabled", "true").lower()
    if printer_enabled_str not in ("true", "1", "yes"):
        logger.info("Receipt printing is disabled in settings. Skipping.")
        return False

    device_path = get_setting("printer_device", Config.PRINTER_DEVICE)
    shop_name = get_setting("shop_name", Config.SHOP_NAME)
    receipt_header = get_setting("receipt_header", f"🛒 {shop_name.upper()} 🛒")
    receipt_footer = get_setting("receipt_footer", "Vielen Dank für deinen Einkauf! 😊")

    tx_id = transaction_data.get("id", "0")
    total_cents = transaction_data.get("total_cents", 0)
    card_name = transaction_data.get("card_name") or "Gast"
    items = transaction_data.get("items", [])

    created_at_str = transaction_data.get("created_at")
    if created_at_str:
        try:
            dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            date_str = dt.strftime("%d.%m.%Y")
            time_str = dt.strftime("%H:%M Uhr")
        except Exception:
            date_str = datetime.now().strftime("%d.%m.%Y")
            time_str = datetime.now().strftime("%H:%M Uhr")
    else:
        date_str = datetime.now().strftime("%d.%m.%Y")
        time_str = datetime.now().strftime("%H:%M Uhr")

    formatted_total = f"{total_cents / 100:.2f}".replace(".", ",") + " €"

    logger.info("Printing receipt for Transaction #%s on device %s...", tx_id, device_path)

    # Check if hardware USB printer device exists
    if not os.path.exists(device_path):
        logger.warning(
            "Printer device path '%s' not found on system. Logging receipt to stdout instead.",
            device_path,
        )
        _log_receipt_text(shop_name, receipt_header, receipt_footer, tx_id, date_str, time_str, card_name, items, formatted_total)
        return False

    try:
        from escpos.printer import File

        printer = File(device_path)

        # Print Header
        printer.set(align="center", font="a", width=2, height=2, bold=True)
        printer.text(f"{shop_name}\n")
        printer.set(align="center", font="a", width=1, height=1, bold=False)
        printer.text(f"{receipt_header}\n")
        printer.text("=" * 32 + "\n")

        # Print Details
        printer.set(align="left")
        printer.text(f"Bon-Nr: #{tx_id}\n")
        printer.text(f"Datum:  {date_str}\n")
        printer.text(f"Zeit:   {time_str}\n")
        printer.text(f"Kunde:  {card_name} 💳\n")
        printer.text("-" * 32 + "\n")

        # Print Items
        for item in items:
            p_name = item.get("product_name", "Artikel")[:16]
            qty = item.get("quantity", 1)
            p_cents = item.get("price_cents", 0) * qty
            p_price = f"{p_cents / 100:.2f}".replace(".", ",") + " €"
            
            line = f"{p_name:<16} {qty:>2}x {p_price:>10}\n"
            printer.text(line)

        printer.text("-" * 32 + "\n")

        # Print Total
        printer.set(align="right", font="a", width=2, height=2, bold=True)
        printer.text(f"SUMME: {formatted_total}\n")
        printer.set(align="center", font="a", width=1, height=1, bold=False)
        printer.text("=" * 32 + "\n")

        # Print Footer
        printer.text(f"Vielen Dank, {card_name}! 😊\n")
        printer.text(f"{receipt_footer}\n")
        printer.text("\n\n\n")
        printer.cut()
        printer.close()

        logger.info("Receipt #%s successfully printed to thermal printer!", tx_id)
        return True

    except Exception as e:
        logger.error("Failed to print to ESC/POS printer on %s: %s", device_path, str(e))
        return False


def _log_receipt_text(shop_name, header, footer, tx_id, date_str, time_str, card_name, items, total_str):
    receipt_lines = [
        "========================================",
        f"        🛒 {shop_name.upper()} 🛒",
        f"        {header}",
        "========================================",
        f"Bon-Nr: #{tx_id}",
        f"Datum:  {date_str}",
        f"Zeit:   {time_str}",
        f"Kunde:  {card_name} 💳",
        "----------------------------------------",
    ]
    for item in items:
        p_name = item.get("product_name", "Artikel")[:18]
        qty = item.get("quantity", 1)
        p_price = f"{(item.get('price_cents', 0) * qty) / 100:.2f}".replace(".", ",") + " €"
        receipt_lines.append(f"{p_name:<18} {qty:>2}x {p_price:>12}")

    receipt_lines.extend([
        "----------------------------------------",
        f"SUMME: {total_str:>31}",
        "========================================",
        f"  Vielen Dank, {card_name}! 😊",
        f"  {footer}",
        "========================================",
    ])
    logger.info("MOCK RECEIPT OUTPUT:\n" + "\n".join(receipt_lines))
