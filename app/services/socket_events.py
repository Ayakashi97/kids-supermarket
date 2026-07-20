import logging
from flask import request
from flask_socketio import SocketIO, emit

logger = logging.getLogger(__name__)
socketio = SocketIO()

# Server state
# Mode can be: 'idle', 'waiting_for_payment', 'waiting_for_registration'
server_state = {
    "mode": "idle",
    "pending_cart": [],
    "registration_card_id": None,
}


def register_socket_events(socket_io: SocketIO):
    @socket_io.on("connect")
    def handle_connect():
        logger.info("Client connected: %s", request.sid)
        emit("status", {"mode": server_state["mode"]})

    @socket_io.on("disconnect")
    def handle_disconnect():
        logger.info("Client disconnected: %s", request.sid)

    @socket_io.on("ping")
    def handle_ping():
        emit("pong", {"status": "ok"})
