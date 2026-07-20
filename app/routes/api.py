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

