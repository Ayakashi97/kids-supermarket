from flask import Blueprint, jsonify
from app.models import Product, Card

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in products])


@api_bp.route("/cards", methods=["GET"])
def get_cards():
    cards = Card.query.filter_by(is_active=True).all()
    return jsonify([c.to_dict() for c in cards])


@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "kinder-supermarkt-backend"})
