import os
import logging
from datetime import datetime, timedelta
from app.config import Config
from app.models import Setting

logger = logging.getLogger(__name__)

# Sliding 1-hour print history rate limiter
PRINT_HISTORY = []
MAX_PRINTS_PER_HOUR = 20


def get_setting(key: str, default_val: str) -> str:
    """Helper to fetch a setting value from DB, with fallback to default."""
    try:
        setting = Setting.query.get(key)
        if setting and setting.value is not None:
            return setting.value
    except Exception as e:
        logger.debug("Could not read setting %s from DB: %s", key, e)
    return default_val


def check_rate_limit() -> tuple[bool, str]:
    """
    Ensures no more than configurable receipts are printed per 60 minutes.
    Returns (allowed: bool, reason: str).
    """
    global PRINT_HISTORY
    now = datetime.now()
    cutoff = now - timedelta(hours=1)
    
    # Keep only prints from the last 1 hour
    PRINT_HISTORY = [t for t in PRINT_HISTORY if t > cutoff]
    
    max_limit_str = get_setting("max_prints_per_hour", "20")
    try:
        max_limit = int(max_limit_str)
    except ValueError:
        max_limit = 20

    if len(PRINT_HISTORY) >= max_limit:
        msg = f"Limit erreicht: Maximal {max_limit} Bons pro Stunde erlaubt! (Schutz vor Papier-Spam) ⏳"
        logger.warning(msg)
        return False, msg

    return True, ""



def print_receipt(transaction_data: dict, check_enabled: bool = True) -> tuple[bool, str]:
    """
    Prints a thermal receipt via python-escpos USB/File device if enabled and connected.
    Enforces a strict 20-receipts-per-hour rate limit.
    Returns (success: bool, message: str).
    """
    # Check rate limit first
    allowed, limit_msg = check_rate_limit()
    if not allowed:
        return False, limit_msg

    # Check if printer is enabled in settings
    if check_enabled:
        printer_enabled_str = get_setting("printer_enabled", "false").lower()
        if printer_enabled_str not in ("true", "1", "yes"):
            msg = "Drucker ist in den Admin-Einstellungen deaktiviert."
            logger.debug(msg)
            return False, msg

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

    # Check if hardware USB printer device exists
    if not os.path.exists(device_path):
        msg = f"Drucker-Gerät '{device_path}' nicht angeschlossen. PDF-Bon steht bereit."
        logger.info(msg)
        return False, msg

    try:
        import json
        from escpos.printer import File
        from app.seed import DEFAULT_RECEIPT_LAYOUT

        printer = File(device_path)

        raw_layout = get_setting("receipt_layout_json", "")
        try:
            receipt_layout = json.loads(raw_layout) if raw_layout else DEFAULT_RECEIPT_LAYOUT
        except Exception:
            receipt_layout = DEFAULT_RECEIPT_LAYOUT

        for block in receipt_layout:
            if not block.get("enabled", True):
                continue

            b_type = block.get("type")
            if b_type == "shop_name":
                printer.set(align="center", font="a", width=2, height=2, bold=True)
                printer.text(f"{shop_name}\n")
            elif b_type == "text":
                align = block.get("align", "center")
                printer.set(align=align, font="a", width=1, height=1, bold=False)
                printer.text(f"{block.get('content', '')}\n")
            elif b_type == "separator":
                style = block.get("style", "dashed")
                if style == "solid":
                    printer.text("=" * 32 + "\n")
                elif style == "blank":
                    printer.text("\n")
                else:
                    printer.text("-" * 32 + "\n")
            elif b_type == "meta":
                printer.set(align="left", font="a", width=1, height=1, bold=False)
                printer.text(f"Bon-Nr: #{tx_id}\n")
                printer.text(f"Datum:  {date_str}\n")
                printer.text(f"Zeit:   {time_str}\n")
            elif b_type == "customer":
                printer.set(align="left", font="a", width=1, height=1, bold=False)
                printer.text(f"Kunde:  {card_name} 💳\n")
            elif b_type == "items":
                printer.set(align="left", font="a", width=1, height=1, bold=False)
                for item in items:
                    p_name = item.get("product_name", "Artikel")[:16]
                    qty = item.get("quantity", 1)
                    p_cents = item.get("price_cents", 0) * qty
                    p_price = f"{p_cents / 100:.2f}".replace(".", ",") + " €"
                    line = f"{p_name:<16} {qty:>2}x {p_price:>10}\n"
                    printer.text(line)
                printer.text("-" * 32 + "\n")
                printer.set(align="right", font="a", width=2, height=2, bold=True)
                printer.text(f"SUMME: {formatted_total}\n")
            elif b_type == "signature":
                title = block.get("title", "UNTERSCHRIFT KUNDE")
                printer.set(align="center", font="a", width=1, height=1, bold=True)
                printer.text(f"{title}\n\n\n")
                printer.text("--------------------------------\n")
            elif b_type == "qrcode":
                base_url = get_setting("base_url", "").strip() or "http://kinderkasse.local:5050"
                qr_target_url = f"{base_url.rstrip('/')}/receipt/{tx_id}"
                try:
                    printer.qr(qr_target_url)
                except Exception:
                    printer.set(align="center", font="a", width=1, height=1, bold=False)
                    printer.text(f"Bon-PDF: {qr_target_url}\n")

        printer.text("\n\n\n")
        printer.cut()
        printer.close()

        # Track timestamp for rate limiting
        PRINT_HISTORY.append(datetime.now())

        success_msg = f"Kassenbon #{tx_id} erfolgreich gedruckt! 🧾 ({len(PRINT_HISTORY)}/{MAX_PRINTS_PER_HOUR} in dieser Stunde)"
        logger.info(success_msg)
        return True, success_msg

    except Exception as e:
        err_msg = f"Fehler beim Drucken: {str(e)}"
        logger.error(err_msg)
        return False, err_msg
