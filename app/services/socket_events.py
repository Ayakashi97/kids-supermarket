import logging
from datetime import datetime, timezone
from flask import request, url_for
from flask_socketio import SocketIO, emit
from app.db import db
from app.models import Card, Transaction, TransactionItem, Product
from app.services.printer import print_receipt

logger = logging.getLogger(__name__)
socketio = SocketIO()

# Server state
# Mode can be: 'idle', 'waiting_for_payment', 'waiting_for_registration'
server_state = {
    "mode": "idle",
    "pending_cart": [],
    "registration_card_id": None,
    "captured_uid": None,
}


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
        logger.info("Payment started with %d items. Waiting for card tap...", len(cart))

        total_cents = sum(item.get("price_cents", 0) * item.get("quantity", 1) for item in cart)

        # Broadcast to all clients (Tablet + Pi #2 Touchscreen Terminal)
        socket_io.emit("waiting_for_payment", {
            "item_count": len(cart),
            "total_cents": total_cents,
            "total_formatted": f"{total_cents / 100:.2f}".replace(".", ",") + " €",
        })

    @socket_io.on("cancel_payment")
    def handle_cancel_payment():
        logger.info("Payment cancelled by client")
        server_state["mode"] = "idle"
        server_state["pending_cart"] = []
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

            # Card Lookup in DB
            card = Card.query.filter_by(nfc_uid=uid).first()

            if not card:
                logger.warning("Unknown card tapped: %s", uid)
                socket_io.emit("payment_error", {"message": "Unbekannte Karte 😕"})
                return

            if not card.is_active:
                logger.warning("Inactive card tapped: %s (%s)", uid, card.name)
                socket_io.emit("payment_error", {"message": "Karte ist inaktiv 🚫"})
                return

            # Valid Card! Process Transaction
            total_cents = sum(item.get("price_cents", 0) * item.get("quantity", 1) for item in cart)

            try:
                transaction = Transaction(
                    total_cents=total_cents,
                    card_id=card.id,
                    nfc_uid=uid,
                    status="completed",
                    created_at=datetime.now(timezone.utc),
                )
                db.session.add(transaction)
                db.session.flush()  # get transaction.id

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

                # Format card image URL
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

                # Reset state
                server_state["mode"] = "idle"
                server_state["pending_cart"] = []

                # Broadcast payment_success to ALL connected clients (Tablet & Touchscreen Terminal)
                socket_io.emit("payment_success", payload)

            except Exception as e:
                db.session.rollback()
                logger.error("Failed to process transaction: %s", str(e), exc_info=True)
                socket_io.emit("payment_error", {"message": "Fehler beim Speichern der Zahlung!"})
            return

        # CASE 3: Idle Mode
        logger.info("Card tapped while server in idle mode: %s", uid)
        card = Card.query.filter_by(nfc_uid=uid).first()
        if card:
            socket_io.emit("card_scanned_info", {
                "name": card.name,
                "nfc_uid": card.nfc_uid,
                "message": f"Hallo {card.name}! 👋"
            })

    @socket_io.on("start_registration")
    def handle_start_registration():
        server_state["mode"] = "waiting_for_registration"
        server_state["captured_uid"] = None
        logger.info("Server entered registration mode")
        socket_io.emit("waiting_for_registration", {"message": "Bitte Karte jetzt an das Lesegerät halten..."})
