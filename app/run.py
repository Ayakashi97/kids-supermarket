from app import create_app
from app.services.socket_events import socketio
from app.config import Config
from app.utils import get_ssl_context

app = create_app()

if __name__ == "__main__":
    ssl_ctx = None
    with app.app_context():
        ssl_ctx = get_ssl_context()
        if ssl_ctx:
            app.logger.info("Starting server with SSL/HTTPS enabled: %s", ssl_ctx)

    socketio.run(
        app,
        host="0.0.0.0",
        port=Config.PORT,
        debug=True,
        allow_unsafe_werkzeug=True,
        ssl_context=ssl_ctx
    )
