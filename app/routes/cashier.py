from flask import Blueprint, render_template, redirect, url_for
from app.models import Product, Category

cashier_bp = Blueprint("cashier", __name__)


def get_setting(key: str, default_val: str) -> str:
    from app.models import Setting
    setting = Setting.query.get(key)
    return setting.value if setting and setting.value is not None else default_val


@cashier_bp.route("/")
def index():
    products = Product.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order, Category.id).all()
    shop_name = get_setting("shop_name", "Kinder-Supermarkt")
    return render_template("cashier.html", products=products, categories=categories, shop_name=shop_name)


@cashier_bp.route("/terminal")
def terminal():
    """Touchscreen terminal view for Raspberry Pi #2 or Smartphone."""
    screen_timeout = get_setting("screen_timeout", "30")
    shop_name = get_setting("shop_name", "Kinder-Supermarkt")
    return render_template("terminal.html", screen_timeout=screen_timeout, shop_name=shop_name)


@cashier_bp.route("/receipt/<int:tx_id>")
def view_receipt(tx_id):
    from app.models import Transaction
    from datetime import datetime

    tx = Transaction.query.get_or_404(tx_id)

    shop_name = get_setting("shop_name", "Kinder-Markt")
    receipt_header = get_setting("receipt_header", f"🛒 {shop_name.upper()} 🛒")
    receipt_footer = get_setting("receipt_footer", "Vielen Dank für deinen Einkauf! 😊")
    show_card_name = get_setting("show_card_name", "true")
    show_date_time = get_setting("show_date_time", "true")
    paper_width = get_setting("paper_width", "58mm")

    dt = tx.created_at or datetime.now()
    date_str = dt.strftime("%d.%m.%Y")
    time_str = dt.strftime("%H:%M Uhr")

    items = [item.to_dict() for item in tx.items]
    card_name = tx.card.name if tx.card else "Gast"
    total_formatted = f"{tx.total_cents / 100:.2f}".replace(".", ",") + " €"

    return render_template(
        "receipt.html",
        tx_id=tx.id,
        shop_name=shop_name,
        receipt_header=receipt_header,
        receipt_footer=receipt_footer,
        show_card_name=show_card_name,
        show_date_time=show_date_time,
        paper_width=paper_width,
        date_str=date_str,
        time_str=time_str,
        card_name=card_name,
        items=items,
        total_formatted=total_formatted,
    )


@cashier_bp.route("/receipt/preview")
def preview_receipt():
    from datetime import datetime

    shop_name = get_setting("shop_name", "Kinder-Markt")
    receipt_header = get_setting("receipt_header", f"🛒 {shop_name.upper()} 🛒")
    receipt_footer = get_setting("receipt_footer", "Vielen Dank für deinen Einkauf! 😊")
    show_card_name = get_setting("show_card_name", "true")
    show_date_time = get_setting("show_date_time", "true")
    paper_width = get_setting("paper_width", "58mm")

    dt = datetime.now()
    date_str = dt.strftime("%d.%m.%Y")
    time_str = dt.strftime("%H:%M Uhr")

    dummy_items = [
        {"product_name": "Brezel", "quantity": 2, "price_cents": 80},
        {"product_name": "Apfel", "quantity": 1, "price_cents": 50},
        {"product_name": "Milch", "quantity": 1, "price_cents": 120},
    ]
    total_formatted = "2,90 €"

    return render_template(
        "receipt.html",
        tx_id="MUSTER-123",
        shop_name=shop_name,
        receipt_header=receipt_header,
        receipt_footer=receipt_footer,
        show_card_name=show_card_name,
        show_date_time=show_date_time,
        paper_width=paper_width,
        date_str=date_str,
        time_str=time_str,
        card_name="Lena",
        items=dummy_items,
        total_formatted=total_formatted,
    )


@cashier_bp.route("/receipt/latest")
def latest_receipt():
    from app.models import Transaction
    tx = Transaction.query.order_by(Transaction.created_at.desc()).first()
    if tx:
        return redirect(url_for("cashier.view_receipt", tx_id=tx.id))
    return redirect(url_for("cashier.preview_receipt"))


@cashier_bp.route("/manifest.json")
def manifest():
    from flask import send_from_directory, current_app
    import os
    static_dir = os.path.join(current_app.root_path, "static")
    return send_from_directory(static_dir, "manifest.json", mimetype="application/manifest+json")


@cashier_bp.route("/manifest-terminal.json")
def terminal_manifest():
    from flask import send_from_directory, current_app
    import os
    static_dir = os.path.join(current_app.root_path, "static")
    return send_from_directory(static_dir, "manifest-terminal.json", mimetype="application/manifest+json")


@cashier_bp.route("/sw.js")
def service_worker():
    from flask import send_from_directory, current_app
    import os
    static_dir = os.path.join(current_app.root_path, "static")
    return send_from_directory(static_dir, "sw.js", mimetype="application/javascript")



