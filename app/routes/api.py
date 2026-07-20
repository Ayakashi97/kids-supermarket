from flask import Blueprint, jsonify
from app.models import Product, Card

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in products])


@api_bp.route("/products/by_nfc/<uid>", methods=["GET"])
def product_by_nfc(uid):
    """Lookup a product by its assigned NFC tag UID (normalized match)."""
    from app.services.socket_events import find_product_by_nfc_uid
    if not uid:
        return jsonify({"found": False}), 400
    product = find_product_by_nfc_uid(uid)
    if not product:
        return jsonify({"found": False, "uid": uid}), 404
    return jsonify({"found": True, "product": product.to_dict()})


@api_bp.route("/cards", methods=["GET"])
def get_cards():
    cards = Card.query.filter_by(is_active=True).all()
    return jsonify([c.to_dict() for c in cards])


@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "kinder-supermarkt-backend"})


@api_bp.route("/nfc_tap", methods=["GET", "POST"])
def nfc_tap():
    """HTTP webhook endpoint allowing iOS Shortcuts or external scripts to simulate an NFC card tap."""
    from flask import request
    from app.services.socket_events import socketio, find_card_by_uid

    uid = request.args.get("uid") or (request.json and request.json.get("uid"))
    if not uid and request.form:
        uid = request.form.get("uid")

    uid = str(uid).strip() if uid else ""
    if not uid:
        return jsonify({"success": False, "error": "Missing 'uid' parameter"}), 400

    card = find_card_by_uid(uid)
    card_name = card.name if card else "Unbekannt"

    # Emit card_tapped event via SocketIO to all connected terminals & cashier UI
    socketio.emit("card_tapped", {"uid": uid})

    return jsonify({
        "success": True,
        "uid": uid,
        "card_found": card is not None,
        "card_name": card_name,
        "message": f"NFC tap triggered for UID '{uid}'"
    })


@api_bp.route("/print_receipt/<int:tx_id>", methods=["GET", "POST"])
def print_receipt_api(tx_id):
    from app.models import Transaction
    from app.services.printer import print_receipt

    tx = Transaction.query.get(tx_id)
    if not tx:
        return jsonify({"success": False, "message": "Transaktion nicht gefunden!"}), 404

    success, message = print_receipt(tx.to_dict(), check_enabled=False)
    return jsonify({"success": success, "message": message})

