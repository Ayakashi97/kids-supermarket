import unittest
from app import create_app
from app.db import db
from app.models import Product, Card, Transaction, TransactionItem
from app.services.socket_events import socketio, server_state


class TestPaymentFlow(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test product & card
        self.product = Product(name="Test Brezel", price_cents=80, emoji="🥨", category="Backwaren")
        self.card = Card(nfc_uid="TEST_CARD_123", name="Test Kinder-Kunde", is_active=True)
        db.session.add(self.product)
        db.session.add(self.card)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_payment_flow(self):
        client = socketio.test_client(self.app)
        self.assertTrue(client.is_connected())

        # 1. Start payment
        cart = [{
            "id": self.product.id,
            "name": self.product.name,
            "price_cents": self.product.price_cents,
            "quantity": 2,
            "emoji": "🥨"
        }]
        client.emit("start_payment", {"cart": cart})

        # Verify server state
        self.assertEqual(server_state["mode"], "waiting_for_payment")
        self.assertEqual(len(server_state["pending_cart"]), 1)

        # 2. Tap card
        client.emit("card_tapped", {"uid": "TEST_CARD_123"})

        # Received events
        received = client.get_received()
        event_names = [e["name"] for e in received]
        self.assertIn("payment_success", event_names)

        # Verify DB transaction saved
        tx = Transaction.query.filter_by(nfc_uid="TEST_CARD_123").first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.total_cents, 160)
        self.assertEqual(tx.card_id, self.card.id)
        self.assertEqual(len(tx.items), 1)
        self.assertEqual(tx.items[0].product_name, "Test Brezel")

    def test_unknown_card_error(self):
        client = socketio.test_client(self.app)
        cart = [{"id": self.product.id, "name": self.product.name, "price_cents": 80, "quantity": 1}]
        client.emit("start_payment", {"cart": cart})

        # Tap unknown card
        client.emit("card_tapped", {"uid": "UNKNOWN_UID_999"})

        received = client.get_received()
        event_names = [e["name"] for e in received]
        self.assertIn("payment_error", event_names)


if __name__ == "__main__":
    unittest.main()
