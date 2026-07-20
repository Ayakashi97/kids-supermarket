from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.config import Config
from app.models import Product, Card, Transaction

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pin = request.form.get("pin", "")
        if pin == Config.ADMIN_PIN:
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
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    products_count = Product.query.count()
    cards_count = Card.query.count()
    transactions_count = Transaction.query.count()
    return render_template(
        "admin/dashboard.html",
        products_count=products_count,
        cards_count=cards_count,
        transactions_count=transactions_count,
    )
