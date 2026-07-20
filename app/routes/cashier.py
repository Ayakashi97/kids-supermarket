from flask import Blueprint, render_template
from app.models import Product

cashier_bp = Blueprint("cashier", __name__)


@cashier_bp.route("/")
def index():
    products = Product.query.filter_by(is_active=True).all()
    return render_template("cashier.html", products=products)


@cashier_bp.route("/terminal")
def terminal():
    """Touchscreen terminal view for Raspberry Pi #2."""
    return render_template("terminal.html")

