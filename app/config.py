import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supermarket-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'supermarkt.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SHOP_NAME = os.getenv("SHOP_NAME", "Kinder-Markt")
    ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")
    PRINTER_DEVICE = os.getenv("PRINTER_DEVICE", "/dev/usb/lp0")
    PORT = int(os.getenv("PORT", 5000))

    UPLOAD_FOLDER = BASE_DIR / "static" / "images"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("true", "1", "yes")

