import logging
from datetime import datetime, timezone
from flask import request
from flask_socketio import SocketIO, emit
from app.db import db
from app.models import Card, Transaction, TransactionItem, Setting
from app.services.printer import print_receipt

logger = logging.getLogger(__name__)
socketio = SocketIO()

# Server state
# Mode can be: 'idle', 'waiting_for_payment', 'waiting_for_pin', 'waiting_for_registration'
server_state = {
    "mode": "idle",
    "pending_cart": [],
    "pending_card_id": None,
    "pending_uid": None,
    "registration_card_id": None,
    "captured_uid": None,
}


def get_setting(key: str, default_val: str) -> str:
    setting = Setting.query.get(key)
    return setting.value if setting and setting.value is not None else default_val


def find_card_by_uid(uid: str) -> Card:
    """Find card by NFC UID using exact match or normalized UID comparison."""
    if not uid:
        return None
    # 1. Exact match
    card = Card.query.filter_by(nfc_uid=uid).first()
    if card:
        return card

    # 2. Normalized match (remove colons, dashes, spaces, lower-case)
    clean_uid = uid.replace(":", "").replace("-", "").replace(" ", "").strip().lower()
    if not clean_uid:
        return None

    all_cards = Card.query.all()
    for c in all_cards:
        if c.nfc_uid:
            c_clean = c.nfc_uid.replace(":", "").replace("-", "").replace(" ", "").strip().lower()
            if c_clean == clean_uid:
                return c
    return None



def process_completed_payment(card: Card, cart: list, socket_io: SocketIO):
    """Saves completed transaction to DB, prints thermal receipt, and broadcasts payment_success."""
    total_cents = sum(item.get("price_cents", 0) * item.get("quantity", 1) for item in cart)

    try:
        transaction = Transaction(
            total_cents=total_cents,
            card_id=card.id,
            nfc_uid=card.nfc_uid,
            status="completed",
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(transaction)
        db.session.flush()

        for item in cart:
            tx_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=item.get("id"),
                product_name=item.get("name", "Unbekanntes Produkt"),
                price_cents=item.get("price_cents", 0),
                quantity=item.get("quantity", 1),
            )
            db.session.add(tx_item)

        card.last_used_at = datetime.now(timezone.utc)
        db.session.commit()
        logger.info("Transaction #%d completed successfully for card holder %s (%d cents)",
                    transaction.id, card.name, total_cents)

        card_image_url = None
        if card.image_path:
            card_image_url = f"/static/{card.image_path}"

        payload = {
            "transaction_id": transaction.id,
            "total_cents": total_cents,
            "total_formatted": f"{total_cents / 100:.2f}".replace(".", ",") + " €",
            "card_name": card.name,
            "card_image_url": card_image_url,
        }

        # Attempt thermal printing
        print_receipt(transaction.to_dict())

        # Reset server state
        server_state["mode"] = "idle"
        server_state["pending_cart"] = []
        server_state["pending_card_id"] = None
        server_state["pending_uid"] = None

        # Broadcast payment_success to ALL connected clients (Tablet & Touchscreen Terminal)
        socket_io.emit("payment_success", payload)

    except Exception as e:
        db.session.rollback()
        logger.error("Failed to process transaction: %s", str(e), exc_info=True)
        socket_io.emit("payment_error", {"message": "Fehler beim Speichern der Zahlung!"})


def register_socket_events(socket_io: SocketIO):
    @socket_io.on("connect")
    def handle_connect():
        logger.info("Client connected: %s", request.sid)
        emit("status", {
            "mode": server_state["mode"],
            "pending_cart_count": len(server_state["pending_cart"]),
        })

    @socket_io.on("disconnect")
    def handle_disconnect():
        logger.info("Client disconnected: %s", request.sid)

    @socket_io.on("ping")
    def handle_ping():
        emit("pong", {"status": "ok"})

    @socket_io.on("start_payment")
    def handle_start_payment(data):
        cart = data.get("cart", [])
        if not cart:
            logger.warning("Attempted payment with empty cart")
            emit("payment_error", {"message": "Warenkorb ist leer!"})
            return

        server_state["mode"] = "waiting_for_payment"
        server_state["pending_cart"] = cart
        server_state["pending_card_id"] = None
        server_state["pending_uid"] = None

        logger.info("Payment started with %d items. Waiting for card tap...", len(cart))
        total_cents = sum(item.get("price_cents", 0) * item.get("quantity", 1) for item in cart)

        active_cards = Card.query.filter_by(is_active=True).order_by(Card.name).all()
        cards_payload = [
            {
                "id": c.id,
                "name": c.name,
                "uid": c.nfc_uid,
                "image_url": f"/static/{c.image_path}" if c.image_path else None,
            }
            for c in active_cards
        ]

        socket_io.emit("waiting_for_payment", {
            "item_count": len(cart),
            "total_cents": total_cents,
            "total_formatted": f"{total_cents / 100:.2f}".replace(".", ",") + " €",
            "nfc_mode": get_setting("nfc_mode", "web_nfc"),
            "cards": cards_payload,
        })

    @socket_io.on("cancel_payment")
    def handle_cancel_payment():
        logger.info("Payment cancelled by client")
        server_state["mode"] = "idle"
        server_state["pending_cart"] = []
        server_state["pending_card_id"] = None
        server_state["pending_uid"] = None
        socket_io.emit("payment_cancelled", {"message": "Zahlung abgebrochen"})

    @socket_io.on("card_tapped")
    def handle_card_tapped(data):
        uid = data.get("uid", "").strip()
        if not uid:
            logger.warning("Received card_tapped event without UID")
            return

        logger.info("NFC Card tapped with UID: %s (Current Server Mode: %s)", uid, server_state["mode"])
        current_mode = server_state["mode"]

        # CASE 1: Card Registration Mode (Admin)
        if current_mode == "waiting_for_registration":
            server_state["captured_uid"] = uid
            server_state["mode"] = "idle"
            logger.info("Card UID %s captured for registration mode", uid)
            socket_io.emit("card_captured", {"uid": uid})
            return

        # CASE 2: Payment Mode
        if current_mode == "waiting_for_payment":
            cart = server_state["pending_cart"]
            if not cart:
                server_state["mode"] = "idle"
                socket_io.emit("payment_error", {"message": "Warenkorb ist leer!"})
                return

            card = find_card_by_uid(uid)

            if not card:
                logger.warning("Unknown card tapped: %s", uid)
                socket_io.emit("payment_error", {"message": "Unbekannte Karte 😕"})
                return

            if not card.is_active:
                logger.warning("Inactive card tapped: %s (%s)", uid, card.name)
                socket_io.emit("payment_error", {"message": "Karte ist inaktiv 🚫"})
                return

            # Read configured PIN mode from Admin settings
            pin_mode = get_setting("pin_mode", "disabled")
            total_cents = sum(item.get("price_cents", 0) * item.get("quantity", 1) for item in cart)
            total_formatted = f"{total_cents / 100:.2f}".replace(".", ",") + " €"

            if pin_mode in ("any_4_digits", "exact_match"):
                server_state["mode"] = "waiting_for_pin"
                server_state["pending_card_id"] = card.id
                server_state["pending_uid"] = uid

                logger.info("Card %s (%s) requires PIN validation (mode: %s). Prompting terminal...",
                            card.name, uid, pin_mode)

                socket_io.emit("prompt_pin", {
                    "card_name": card.name,
                    "total_cents": total_cents,
                    "total_formatted": total_formatted,
                    "pin_mode": pin_mode,
                })
                return

            # Direct payment if PIN mode disabled
            process_completed_payment(card, cart, socket_io)
            return

        # CASE 3: Idle Mode
        logger.info("Card tapped while server in idle mode: %s", uid)
        card = find_card_by_uid(uid)
        if card:
            socket_io.emit("card_scanned_info", {
                "name": card.name,
                "nfc_uid": card.nfc_uid,
                "message": f"Hallo {card.name}! 👋"
            })

    @socket_io.on("submit_pin")
    def handle_submit_pin(data):
        entered_pin = str(data.get("pin", "")).strip()
        current_mode = server_state["mode"]

        if current_mode != "waiting_for_pin":
            logger.warning("Received submit_pin event while not in waiting_for_pin mode")
            return

        card_id = server_state.get("pending_card_id")
        card = Card.query.get(card_id) if card_id else None

        if not card:
            server_state["mode"] = "idle"
            socket_io.emit("payment_error", {"message": "Kartenfehler! Bitte erneut versuchen."})
            return

        pin_mode = get_setting("pin_mode", "disabled")
        logger.info("PIN %s submitted for card %s (pin_mode: %s)", entered_pin, card.name, pin_mode)

        if pin_mode == "any_4_digits":
            if len(entered_pin) != 4 or not entered_pin.isdigit():
                logger.warning("Invalid 4-digit PIN entered: '%s'", entered_pin)
                socket_io.emit("pin_error", {"message": "Bitte 4 Zahlen eingeben! 🔢"})
                return
        elif pin_mode == "exact_match":
            expected_pin = card.pin or "1234"
            if entered_pin != expected_pin:
                logger.warning("Incorrect PIN for card %s: entered '%s', expected '%s'",
                               card.name, entered_pin, expected_pin)
                socket_io.emit("pin_error", {"message": "Falsche Geheimzahl! ❌ Versuche es nochmal."})
                return

        # PIN verified! Process payment
        process_completed_payment(card, server_state["pending_cart"], socket_io)

    @socket_io.on("start_registration")
    def handle_start_registration():
        server_state["mode"] = "waiting_for_registration"
        server_state["captured_uid"] = None
        logger.info("Server entered registration mode")
        socket_io.emit("waiting_for_registration", {"message": "Bitte Karte jetzt an das Lesegerät halten..."})
