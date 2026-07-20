import logging
from app.db import db
from app.models import Product

logger = logging.getLogger(__name__)

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


def seed_default_products():
    """Seeds default German supermarket products if database is empty."""
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
