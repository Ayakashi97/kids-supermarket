import json
import logging
from app.db import db
from app.models import Product, Card, Category, Setting

logger = logging.getLogger(__name__)

DEFAULT_RECEIPT_LAYOUT = [
    {"id": "shop_name", "type": "shop_name", "enabled": True, "align": "center", "size": "large"},
    {"id": "header_text", "type": "text", "enabled": True, "align": "center", "content": "Vielen Dank für deinen Einkauf!"},
    {"id": "sep_1", "type": "separator", "enabled": True, "style": "dashed"},
    {"id": "meta_info", "type": "meta", "enabled": True, "show_tx_id": True, "show_datetime": True},
    {"id": "card_info", "type": "customer", "enabled": True, "show_card_name": True},
    {"id": "sep_2", "type": "separator", "enabled": True, "style": "dashed"},
    {"id": "items_table", "type": "items", "enabled": True},
    {"id": "sep_3", "type": "separator", "enabled": True, "style": "solid"},
    {"id": "signature", "type": "signature", "enabled": True, "title": "UNTERSCHRIFT KUNDE"},
    {"id": "footer_text", "type": "text", "enabled": True, "align": "center", "content": "Bis zum nächsten Mal!"},
    {"id": "qr_code", "type": "qrcode", "enabled": True, "content": "tx_id"}
]

DEFAULT_CATEGORIES = [
    {"name": "Obst & Gemüse", "emoji": "🍎", "sort_order": 1},
    {"name": "Backwaren", "emoji": "🥨", "sort_order": 2},
    {"name": "Milchprodukte", "emoji": "🥛", "sort_order": 3},
    {"name": "Getränke", "emoji": "🧃", "sort_order": 4},
    {"name": "Süßes", "emoji": "🍫", "sort_order": 5},
    {"name": "Sonstiges", "emoji": "📦", "sort_order": 6},
]

DEFAULT_PRODUCTS = [
    {"name": "Brezel", "price_cents": 80, "emoji": "🥨", "category": "Backwaren"},
    {"name": "Apfel", "price_cents": 50, "emoji": "🍎", "category": "Obst & Gemüse"},
    {"name": "Banane", "price_cents": 40, "emoji": "🍌", "category": "Obst & Gemüse"},
    {"name": "Milch", "price_cents": 120, "emoji": "🥛", "category": "Milchprodukte"},
    {"name": "Käse", "price_cents": 150, "emoji": "🧀", "category": "Milchprodukte"},
    {"name": "Brot", "price_cents": 180, "emoji": "🍞", "category": "Backwaren"},
    {"name": "Saft", "price_cents": 100, "emoji": "🧃", "category": "Getränke"},
    {"name": "Karotte", "price_cents": 30, "emoji": "🥕", "category": "Obst & Gemüse"},
    {"name": "Schokolade", "price_cents": 90, "emoji": "🍫", "category": "Süßes"},
    {"name": "Eier", "price_cents": 200, "emoji": "🥚", "category": "Milchprodukte"},
    {"name": "Muffin", "price_cents": 110, "emoji": "🧁", "category": "Backwaren"},
    {"name": "Erdbeeren", "price_cents": 180, "emoji": "🍓", "category": "Obst & Gemüse"},
]

DEFAULT_TEST_CARDS = [
    {"nfc_uid": "TEST_LENA_123", "name": "Lena 👧"},
    {"nfc_uid": "TEST_PAPA_456", "name": "Papa 👨"},
]


def seed_default_products():
    """Seeds default German supermarket categories, products & settings if empty."""
    if Category.query.first() is None:
        logger.info("Seeding default categories...")
        for cat in DEFAULT_CATEGORIES:
            c = Category(name=cat["name"], emoji=cat["emoji"], sort_order=cat["sort_order"], is_active=True)
            db.session.add(c)
        db.session.commit()
        logger.info("Successfully seeded default categories.")

    if Product.query.first() is None:
        logger.info("Database empty. Seeding default German products...")
        for item in DEFAULT_PRODUCTS:
            product = Product(
                name=item["name"],
                price_cents=item["price_cents"],
                emoji=item["emoji"],
                category=item["category"],
                is_active=True,
            )
            db.session.add(product)
        db.session.commit()
        logger.info("Successfully seeded %d default products.", len(DEFAULT_PRODUCTS))

    if Card.query.first() is None:
        logger.info("Seeding default test customer cards for development...")
        for c_item in DEFAULT_TEST_CARDS:
            card = Card(
                nfc_uid=c_item["nfc_uid"],
                name=c_item["name"],
                is_active=True,
            )
            db.session.add(card)
        db.session.commit()
        logger.info("Successfully seeded test customer cards.")

    # Seed default receipt layout setting if not present
    if Setting.query.filter_by(key="receipt_layout_json").first() is None:
        logger.info("Seeding default receipt_layout_json setting...")
        s = Setting(key="receipt_layout_json", value=json.dumps(DEFAULT_RECEIPT_LAYOUT))
        db.session.add(s)
        db.session.commit()
        logger.info("Successfully seeded default receipt layout.")
