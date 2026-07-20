from datetime import datetime, timezone
from app.db import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=True, default="📦")
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)  # Stored in cents (e.g. 150 = 1,50 €)
    emoji = db.Column(db.String(10), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False, default="Sonstiges")
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price_cents": self.price_cents,
            "price_formatted": f"{self.price_cents / 100:.2f}".replace(".", ",") + " €",
            "emoji": self.emoji,
            "image_path": self.image_path,
            "category": self.category,
            "is_active": self.is_active,
        }


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    nfc_uid = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    pin = db.Column(db.String(10), nullable=True)  # Optional 4-digit PIN for card holder
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_used_at = db.Column(db.DateTime, nullable=True)

    transactions = db.relationship("Transaction", backref="card", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nfc_uid": self.nfc_uid,
            "name": self.name,
            "pin": self.pin,
            "image_path": self.image_path,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    total_cents = db.Column(db.Integer, nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=True)
    nfc_uid = db.Column(db.String(50), nullable=True)
    signature_data = db.Column(db.Text, nullable=True)  # Base64 PNG image of drawn signature
    status = db.Column(db.String(20), default="completed", nullable=False)

    items = db.relationship(
        "TransactionItem", backref="transaction", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_cents": self.total_cents,
            "total_formatted": f"{self.total_cents / 100:.2f}".replace(".", ",") + " €",
            "card_id": self.card_id,
            "card_name": self.card.name if self.card else None,
            "nfc_uid": self.nfc_uid,
            "signature_data": self.signature_data,
            "status": self.status,
            "items": [item.to_dict() for item in self.items],
        }


class TransactionItem(db.Model):
    __tablename__ = "transaction_items"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(
        db.Integer, db.ForeignKey("transactions.id"), nullable=False
    )
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    product_name = db.Column(db.String(100), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price_cents": self.price_cents,
            "quantity": self.quantity,
            "total_cents": self.price_cents * self.quantity,
        }


class Setting(db.Model):
    __tablename__ = "settings"

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)
