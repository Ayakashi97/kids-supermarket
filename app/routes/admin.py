import os
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.config import Config
from app.db import db
from app.models import Product, Card, Transaction, Setting
from app.services.socket_events import server_state, socketio

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def is_logged_in():
    return session.get("admin_logged_in") is True


def get_setting(key: str, default_val: str) -> str:
    setting = Setting.query.get(key)
    return setting.value if setting and setting.value is not None else default_val


def set_setting(key: str, val: str):
    setting = Setting.query.get(key)
    if not setting:
        setting = Setting(key=key, value=val)
        db.session.add(setting)
    else:
        setting.value = val
    db.session.commit()


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pin = request.form.get("pin", "")
        current_pin = get_setting("admin_pin", Config.ADMIN_PIN)
        if pin == current_pin:
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Falsche PIN!", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    products_count = Product.query.count()
    cards_count = Card.query.count()
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    total_revenue_cents = db.session.query(db.func.sum(Transaction.total_cents)).scalar() or 0

    return render_template(
        "admin/dashboard.html",
        products_count=products_count,
        cards_count=cards_count,
        transactions_count=Transaction.query.count(),
        total_revenue_formatted=f"{total_revenue_cents / 100:.2f}".replace(".", ",") + " €",
        recent_transactions=transactions,
    )


# --- Product Management ---
@admin_bp.route("/products", methods=["GET", "POST"])
def products():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_euros = float(request.form.get("price", "0.0").replace(",", "."))
        price_cents = int(round(price_euros * 100))
        category = request.form.get("category", "Sonstiges")
        emoji = request.form.get("emoji", "🛒").strip()

        image_path = None
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_dir = os.path.join(current_app.root_path, "static", "images", "products")
                os.makedirs(save_dir, exist_ok=True)
                file.save(os.path.join(save_dir, filename))
                image_path = f"images/products/{filename}"

        product = Product(
            name=name,
            price_cents=price_cents,
            category=category,
            emoji=emoji,
            image_path=image_path,
            is_active=True,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Produkt '{name}' erfolgreich hinzugefügt!", "success")
        return redirect(url_for("admin.products"))

    all_products = Product.query.order_by(Product.category, Product.name).all()
    return render_template("admin/products.html", products=all_products)


@admin_bp.route("/products/toggle/<int:product_id>")
def toggle_product(product_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/delete/<int:product_id>")
def delete_product(product_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Produkt gelöscht!", "info")
    return redirect(url_for("admin.products"))


# --- Card Management (NFC Registration & Photos) ---
@admin_bp.route("/cards", methods=["GET", "POST"])
def cards():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        nfc_uid = request.form.get("nfc_uid", "").strip()
        name = request.form.get("name", "").strip()

        if not nfc_uid or not name:
            flash("Bitte Name und NFC UID angeben!", "danger")
            return redirect(url_for("admin.cards"))

        # Check existing
        existing = Card.query.filter_by(nfc_uid=nfc_uid).first()
        if existing:
            flash(f"NFC-Karte mit UID {nfc_uid} ist bereits registriert ({existing.name})!", "danger")
            return redirect(url_for("admin.cards"))

        image_path = None
        if "photo_file" in request.files:
            file = request.files["photo_file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_dir = os.path.join(current_app.root_path, "static", "images", "cards")
                os.makedirs(save_dir, exist_ok=True)
                file.save(os.path.join(save_dir, filename))
                image_path = f"images/cards/{filename}"

        pin = request.form.get("pin", "").strip() or None

        card = Card(
            nfc_uid=nfc_uid,
            name=name,
            pin=pin,
            image_path=image_path,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(card)
        db.session.commit()
        flash(f"Karte für '{name}' (UID: {nfc_uid}) erfolgreich registriert! 🎉", "success")
        return redirect(url_for("admin.cards"))

    all_cards = Card.query.order_by(Card.name).all()
    return render_template("admin/cards.html", cards=all_cards)


@admin_bp.route("/cards/toggle/<int:card_id>")
def toggle_card(card_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    card = Card.query.get_or_404(card_id)
    card.is_active = not card.is_active
    db.session.commit()
    return redirect(url_for("admin.cards"))


@admin_bp.route("/cards/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    card = Card.query.get_or_404(card_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        pin = request.form.get("pin", "").strip() or None

        if not name:
            flash("Bitte Name angeben!", "danger")
            return redirect(url_for("admin.edit_card", card_id=card.id))

        if "photo_file" in request.files:
            file = request.files["photo_file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_dir = os.path.join(current_app.root_path, "static", "images", "cards")
                os.makedirs(save_dir, exist_ok=True)
                file.save(os.path.join(save_dir, filename))
                card.image_path = f"images/cards/{filename}"

        card.name = name
        card.pin = pin
        db.session.commit()
        flash(f"Kundenkarte '{card.name}' erfolgreich aktualisiert! 🎉", "success")
        return redirect(url_for("admin.cards"))

    return render_template("admin/edit_card.html", card=card)


@admin_bp.route("/cards/delete/<int:card_id>")
def delete_card(card_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    flash("Kundenkarte gelöscht!", "info")
    return redirect(url_for("admin.cards"))


# --- Settings Route ---
@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        shop_name = request.form.get("shop_name", Config.SHOP_NAME)
        admin_pin = request.form.get("admin_pin", Config.ADMIN_PIN)
        pin_mode = request.form.get("pin_mode", "disabled")
        printer_enabled = request.form.get("printer_enabled", "true")
        printer_device = request.form.get("printer_device", Config.PRINTER_DEVICE)
        receipt_header = request.form.get("receipt_header", "")
        receipt_footer = request.form.get("receipt_footer", "")
        show_card_name = request.form.get("show_card_name", "true")
        show_date_time = request.form.get("show_date_time", "true")
        paper_width = request.form.get("paper_width", "58mm")

        set_setting("shop_name", shop_name)
        set_setting("admin_pin", admin_pin)
        set_setting("pin_mode", pin_mode)
        set_setting("printer_enabled", printer_enabled)
        set_setting("printer_device", printer_device)
        set_setting("receipt_header", receipt_header)
        set_setting("receipt_footer", receipt_footer)
        set_setting("show_card_name", show_card_name)
        set_setting("show_date_time", show_date_time)
        set_setting("paper_width", paper_width)

        flash("Einstellungen & Terminal PIN-Modus erfolgreich gespeichert!", "success")
        return redirect(url_for("admin.settings"))

    current_settings = {
        "shop_name": get_setting("shop_name", Config.SHOP_NAME),
        "admin_pin": get_setting("admin_pin", Config.ADMIN_PIN),
        "pin_mode": get_setting("pin_mode", "disabled"),
        "printer_enabled": get_setting("printer_enabled", "true"),
        "printer_device": get_setting("printer_device", Config.PRINTER_DEVICE),
        "receipt_header": get_setting("receipt_header", "🛒 WILLKOMMEN IM KINDER-MARKT 🛒"),
        "receipt_footer": get_setting("receipt_footer", "Vielen Dank für deinen Einkauf! 😊"),
        "show_card_name": get_setting("show_card_name", "true"),
        "show_date_time": get_setting("show_date_time", "true"),
        "paper_width": get_setting("paper_width", "58mm"),
    }
    return render_template("admin/settings.html", settings=current_settings)



# --- Transaction History Route ---
@admin_bp.route("/transactions")
def transactions():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    all_tx = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template("admin/transactions.html", transactions=all_tx)
