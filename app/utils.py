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
    """Return (cert_path, key_path) if SSL is configured, enabled, files exist AND key values match, else None."""
    import os
    import ssl
    from app.models import Setting

    try:
        ssl_enabled = Setting.query.get("ssl_enabled")
        if not ssl_enabled or ssl_enabled.value != "true":
            return None

        cert = Setting.query.get("ssl_cert_path")
        key = Setting.query.get("ssl_key_path")

        if cert and key and cert.value and key.value:
            cert_path, key_path = cert.value, key.value
            if os.path.exists(cert_path) and os.path.exists(key_path):
                try:
                    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
                    return (cert_path, key_path)
                except Exception as ssl_err:
                    logger.error("SSL Certificate/Key error (key mismatch or invalid): %s", ssl_err)
                    return None
            else:
                logger.warning("SSL files not found on disk: %s or %s", cert_path, key_path)
    except Exception as e:
        logger.debug("Could not read SSL configuration from DB: %s", e)
    return None
