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
