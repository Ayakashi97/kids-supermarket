from app import create_app
from app.services.socket_events import socketio
from app.config import Config

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=Config.PORT,
        debug=True,
        allow_unsafe_werkzeug=True
    )
