import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

# Ensure data directory exists
data_dir = BASE_DIR / "data"
data_dir.mkdir(parents=True, exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supermarket-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{data_dir / 'supermarkt.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SHOP_NAME = os.getenv("SHOP_NAME", "Kinder-Supermarkt")
    ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")
    PRINTER_DEVICE = os.getenv("PRINTER_DEVICE", "/dev/usb/lp0")
    HTTP_PORT = int(os.getenv("HTTP_PORT", 80))
    HTTPS_PORT = int(os.getenv("HTTPS_PORT", 443))

    UPLOAD_FOLDER = BASE_DIR / "static" / "images"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("true", "1", "yes")
