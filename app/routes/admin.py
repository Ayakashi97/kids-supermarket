import os
import logging
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.config import Config
from app.db import db
from app.models import Product, Card, Transaction, Setting, Category
from app.services.socket_events import server_state, socketio

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def is_logged_in():
    return session.get("admin_logged_in") is True


from app.utils import get_setting


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

    from app.db import db
    from sqlalchemy import func

    products_count = Product.query.count()
    active_products_count = Product.query.filter_by(is_active=True).count()
    cards_count = Card.query.count()
    transactions_count = Transaction.query.count()
    total_revenue_cents = db.session.query(func.sum(Transaction.total_cents)).scalar() or 0

    # Recent transactions (last 5)
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()

    # Top 5 products by quantity sold
    from app.models import TransactionItem
    top_products = (
        db.session.query(
            TransactionItem.product_name,
            func.sum(TransactionItem.quantity).label("total_qty"),
            func.sum(TransactionItem.price_cents * TransactionItem.quantity).label("total_revenue")
        )
        .group_by(TransactionItem.product_name)
        .order_by(func.sum(TransactionItem.quantity).desc())
        .limit(5)
        .all()
    )

    # Revenue by category (from TransactionItems joined with product name)
    category_stats = (
        db.session.query(
            TransactionItem.product_name,
            func.sum(TransactionItem.price_cents * TransactionItem.quantity).label("cat_revenue")
        )
        .group_by(TransactionItem.product_name)
        .all()
    )

    # Revenue per day for the last 7 days — use func.date() for SQLite compatibility
    # (SQLite stores datetimes as strings; cast(..., Date) fails with fromisoformat error)
    from datetime import datetime, timedelta, timezone, date as date_type
    raw_daily = (
        db.session.query(
            func.date(Transaction.created_at).label("day_str"),
            func.sum(Transaction.total_cents).label("daily_total")
        )
        .filter(Transaction.created_at.isnot(None))
        .group_by(func.date(Transaction.created_at))
        .order_by(func.date(Transaction.created_at).desc())
        .limit(7)
        .all()
    )
    # Convert string dates to Python date objects and put in chronological order
    daily_revenue = []
    for row in reversed(raw_daily):
        try:
            day_obj = date_type.fromisoformat(row.day_str) if row.day_str else None
        except Exception:
            day_obj = None
        daily_revenue.append({"day": day_obj, "daily_total": row.daily_total or 0})


    # Most active cards
    top_cards = (
        db.session.query(
            Card.name,
            func.count(Transaction.id).label("tx_count"),
            func.sum(Transaction.total_cents).label("card_revenue")
        )
        .join(Transaction, Transaction.card_id == Card.id)
        .group_by(Card.id, Card.name)
        .order_by(func.count(Transaction.id).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        products_count=products_count,
        active_products_count=active_products_count,
        cards_count=cards_count,
        transactions_count=transactions_count,
        total_revenue_formatted=f"{total_revenue_cents / 100:.2f}".replace(".", ",") + " €",
        recent_transactions=recent_transactions,
        top_products=top_products,
        daily_revenue=daily_revenue,
        top_cards=top_cards,
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

        nfc_uid = request.form.get("nfc_uid", "").strip() or None

        if nfc_uid:
            existing_nfc = Product.query.filter_by(nfc_uid=nfc_uid).first()
            if existing_nfc:
                flash(f"NFC-Tag '{nfc_uid}' ist bereits dem Produkt '{existing_nfc.name}' zugewiesen!", "danger")
                return redirect(url_for("admin.products"))

        cat_obj = Category.query.filter_by(name=category).first()

        product = Product(
            name=name,
            price_cents=price_cents,
            category=category,
            category_id=cat_obj.id if cat_obj else None,
            emoji=emoji,
            image_path=image_path,
            nfc_uid=nfc_uid,
            is_active=True,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Produkt '{name}' erfolgreich hinzugefügt!", "success")
        return redirect(url_for("admin.products"))


    all_products = Product.query.order_by(Product.category, Product.name).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template("admin/products.html", products=all_products, categories=categories)


# --- Category Management ---
@admin_bp.route("/categories", methods=["GET", "POST"])
def categories():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        emoji = request.form.get("emoji", "📦").strip()
        sort_order = int(request.form.get("sort_order", "0"))

        if not name:
            flash("Bitte Name der Kategorie eingeben!", "danger")
            return redirect(url_for("admin.categories"))

        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash(f"Kategorie '{name}' existiert bereits!", "danger")
            return redirect(url_for("admin.categories"))

        category = Category(name=name, emoji=emoji, sort_order=sort_order, is_active=True)
        db.session.add(category)
        db.session.commit()
        flash(f"Kategorie '{name}' erfolgreich hinzugefügt! 🎉", "success")
        return redirect(url_for("admin.categories"))

    all_cats = Category.query.order_by(Category.sort_order, Category.id).all()
    return render_template("admin/categories.html", categories=all_cats)


@admin_bp.route("/categories/toggle/<int:cat_id>")
def toggle_category(cat_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    cat = Category.query.get_or_404(cat_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    return redirect(url_for("admin.categories"))


@admin_bp.route("/categories/edit/<int:cat_id>", methods=["GET", "POST"])
def edit_category(cat_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    cat = Category.query.get_or_404(cat_id)

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        emoji = request.form.get("emoji", "📦").strip()
        sort_order = int(request.form.get("sort_order", "0"))

        if not new_name:
            flash("Bitte Name der Kategorie eingeben!", "danger")
            return redirect(url_for("admin.edit_category", cat_id=cat.id))

        if new_name != cat.name:
            existing = Category.query.filter_by(name=new_name).first()
            if existing:
                flash(f"Kategorie '{new_name}' existiert bereits!", "danger")
                return redirect(url_for("admin.edit_category", cat_id=cat.id))

            Product.query.filter_by(category=cat.name).update({"category": new_name})

        cat.name = new_name
        cat.emoji = emoji
        cat.sort_order = sort_order
        db.session.commit()
        flash(f"Kategorie '{cat.name}' erfolgreich aktualisiert! 🎉", "success")
        return redirect(url_for("admin.categories"))

    return render_template("admin/edit_category.html", category=cat)


@admin_bp.route("/categories/delete/<int:cat_id>")
def delete_category(cat_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    cat = Category.query.get_or_404(cat_id)
    product_count = Product.query.filter_by(category=cat.name).count()
    if product_count > 0:
        flash(f"Kategorie '{cat.name}' kann nicht gelöscht werden, da noch {product_count} Produkte zugeordnet sind!", "danger")
        return redirect(url_for("admin.categories"))

    db.session.delete(cat)
    db.session.commit()
    flash(f"Kategorie '{cat.name}' gelöscht!", "info")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_euros = float(request.form.get("price", "0.0").replace(",", "."))
        price_cents = int(round(price_euros * 100))
        category = request.form.get("category", "Sonstiges")
        emoji = request.form.get("emoji", "🛒").strip()

        nfc_uid = request.form.get("nfc_uid", "").strip() or None

        if not name:
            flash("Bitte Produktname angeben!", "danger")
            return redirect(url_for("admin.edit_product", product_id=product.id))

        if nfc_uid:
            existing_nfc = Product.query.filter(
                Product.nfc_uid == nfc_uid,
                Product.id != product.id
            ).first()
            if existing_nfc:
                flash(f"NFC-Tag '{nfc_uid}' ist bereits dem Produkt '{existing_nfc.name}' zugewiesen!", "danger")
                return redirect(url_for("admin.edit_product", product_id=product.id))

        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_dir = os.path.join(current_app.root_path, "static", "images", "products")
                os.makedirs(save_dir, exist_ok=True)
                file.save(os.path.join(save_dir, filename))
                product.image_path = f"images/products/{filename}"

        cat_obj = Category.query.filter_by(name=category).first()

        product.name = name
        product.price_cents = price_cents
        product.category = category
        product.category_id = cat_obj.id if cat_obj else None
        product.emoji = emoji
        product.nfc_uid = nfc_uid

        db.session.commit()
        flash(f"Produkt '{product.name}' erfolgreich aktualisiert! 🎉", "success")
        return redirect(url_for("admin.products"))

    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template("admin/edit_product.html", product=product, categories=categories)


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
    # Delete associated image file from disk
    if product.image_path:
        img_full_path = os.path.join(current_app.root_path, "static", product.image_path)
        if os.path.isfile(img_full_path):
            try:
                os.remove(img_full_path)
            except OSError as e:
                logger.warning("Could not delete product image %s: %s", img_full_path, e)
    db.session.delete(product)
    db.session.commit()
    flash("Produkt gelöscht!", "info")
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/clear_nfc/<int:product_id>")
def clear_product_nfc(product_id):
    """Remove the NFC tag assignment from a product."""
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    product = Product.query.get_or_404(product_id)
    product.nfc_uid = None
    db.session.commit()
    flash(f"NFC-Tag von '{product.name}' entfernt.", "info")
    return redirect(url_for("admin.edit_product", product_id=product_id))


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
    # Delete associated photo file from disk
    if card.image_path:
        img_full_path = os.path.join(current_app.root_path, "static", card.image_path)
        if os.path.isfile(img_full_path):
            try:
                os.remove(img_full_path)
            except OSError as e:
                logger.warning("Could not delete card image %s: %s", img_full_path, e)
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
        nfc_mode = request.form.get("nfc_mode", "web_nfc")
        printer_enabled = request.form.get("printer_enabled", "false")
        print_mode = request.form.get("print_mode", "ask_cashier")
        max_prints_per_hour = request.form.get("max_prints_per_hour", "20")
        printer_device = request.form.get("printer_device", Config.PRINTER_DEVICE)
        receipt_header = request.form.get("receipt_header", "")
        receipt_footer = request.form.get("receipt_footer", "")
        show_card_name = request.form.get("show_card_name", "true")
        show_date_time = request.form.get("show_date_time", "true")
        paper_width = request.form.get("paper_width", "58mm")
        screen_timeout = request.form.get("screen_timeout", "30")
        show_nfc_toast = request.form.get("show_nfc_toast", "true")
        base_url = request.form.get("base_url", "").strip()
        receipt_layout_json = request.form.get("receipt_layout_json", "")

        set_setting("shop_name", shop_name)
        set_setting("admin_pin", admin_pin)
        set_setting("pin_mode", pin_mode)
        set_setting("nfc_mode", nfc_mode)
        set_setting("scanner_mode", request.form.get("scanner_mode", "disabled"))
        set_setting("printer_enabled", printer_enabled)
        set_setting("print_mode", print_mode)
        set_setting("max_prints_per_hour", max_prints_per_hour)
        set_setting("printer_device", printer_device)
        set_setting("receipt_header", receipt_header)
        set_setting("receipt_footer", receipt_footer)
        set_setting("show_card_name", show_card_name)
        set_setting("show_date_time", show_date_time)
        set_setting("paper_width", paper_width)
        set_setting("screen_timeout", screen_timeout)
        set_setting("show_nfc_toast", show_nfc_toast)
        set_setting("base_url", base_url)
        if receipt_layout_json:
            set_setting("receipt_layout_json", receipt_layout_json)

        flash("Einstellungen & Bon-Template erfolgreich gespeichert!", "success")
        return redirect(url_for("admin.settings"))

    from app.seed import DEFAULT_RECEIPT_LAYOUT
    import json
    default_json = json.dumps(DEFAULT_RECEIPT_LAYOUT)

    current_settings = {
        "shop_name": get_setting("shop_name", Config.SHOP_NAME),
        "admin_pin": get_setting("admin_pin", Config.ADMIN_PIN),
        "pin_mode": get_setting("pin_mode", "disabled"),
        "nfc_mode": get_setting("nfc_mode", "web_nfc"),
        "scanner_mode": get_setting("scanner_mode", "disabled"),
        "printer_enabled": get_setting("printer_enabled", "false"),
        "print_mode": get_setting("print_mode", "ask_cashier"),
        "max_prints_per_hour": get_setting("max_prints_per_hour", "20"),
        "printer_device": get_setting("printer_device", Config.PRINTER_DEVICE),
        "receipt_header": get_setting("receipt_header", "🛒 WILLKOMMEN IM KINDER-MARKT 🛒"),
        "receipt_footer": get_setting("receipt_footer", "Vielen Dank für deinen Einkauf! 😊"),
        "show_card_name": get_setting("show_card_name", "true"),
        "show_date_time": get_setting("show_date_time", "true"),
        "paper_width": get_setting("paper_width", "58mm"),
        "screen_timeout": get_setting("screen_timeout", "30"),
        "show_nfc_toast": get_setting("show_nfc_toast", "true"),
        "base_url": get_setting("base_url", ""),
        "receipt_layout_json": get_setting("receipt_layout_json", default_json),
    }

    return render_template("admin/settings.html", settings=current_settings)



# --- Transaction History Route ---
@admin_bp.route("/transactions")
def transactions():
    if not is_logged_in():
        return redirect(url_for("admin.login"))

    all_tx = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template("admin/transactions.html", transactions=all_tx)


@admin_bp.route("/transactions/delete/<int:tx_id>")
def delete_transaction(tx_id):
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    tx = Transaction.query.get_or_404(tx_id)
    db.session.delete(tx)
    db.session.commit()
    flash(f"Einkauf #{tx_id} gelöscht!", "info")
    return redirect(url_for("admin.transactions"))


@admin_bp.route("/transactions/clear")
def clear_transactions():
    if not is_logged_in():
        return redirect(url_for("admin.login"))
    Transaction.query.delete()
    db.session.commit()
    flash("Alle Einkäufe wurden zurückgesetzt!", "info")
    return redirect(url_for("admin.transactions"))
