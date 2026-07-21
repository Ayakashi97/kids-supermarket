"""Shared utility functions for Kinder-Supermarkt."""
import logging

logger = logging.getLogger(__name__)


def get_setting(key: str, default_val: str) -> str:
    """Fetch a setting value from DB, with fallback to default."""
    try:
        from app.models import Setting
        setting = Setting.query.get(key)
        if setting and setting.value is not None:
            return setting.value
    except Exception as e:
        logger.debug("Could not read setting %s from DB: %s", key, e)
    return default_val


def format_cents(cents: int) -> str:
    """Format integer cents as German currency string, e.g. 150 -> '1,50 €'."""
    return f"{cents / 100:.2f}".replace(".", ",") + " €"


def get_ssl_context():
    """Return (cert_path, key_path) if SSL is configured, enabled and files exist, else None."""
    import os
    from app.models import Setting

    try:
        ssl_enabled = Setting.query.get("ssl_enabled")
        if not ssl_enabled or ssl_enabled.value != "true":
            return None

        cert = Setting.query.get("ssl_cert_path")
        key = Setting.query.get("ssl_key_path")

        if cert and key and cert.value and key.value:
            if os.path.exists(cert.value) and os.path.exists(key.value):
                return (cert.value, key.value)
            else:
                logger.warning("SSL files not found on disk: %s or %s", cert.value, key.value)
    except Exception as e:
        logger.debug("Could not read SSL configuration from DB: %s", e)
    return None
