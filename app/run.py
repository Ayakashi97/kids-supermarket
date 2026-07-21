from app import create_app
from app.services.socket_events import socketio
from app.config import Config
from app.utils import get_ssl_context

app = create_app()

if __name__ == "__main__":
    certfile = None
    keyfile = None
    with app.app_context():
        ssl_ctx = get_ssl_context()
        if ssl_ctx:
            certfile, keyfile = ssl_ctx
            app.logger.info("Starting server with SSL/HTTPS enabled: cert=%s, key=%s", certfile, keyfile)

    run_kwargs = {
        "host": "0.0.0.0",
        "port": Config.PORT,
        "debug": True,
        "allow_unsafe_werkzeug": True
    }
    if certfile and keyfile:
        run_kwargs["certfile"] = certfile
        run_kwargs["keyfile"] = keyfile

    socketio.run(app, **run_kwargs)
