import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from app import create_app
from app.services.socket_events import socketio
from app.config import Config
from app.utils import get_ssl_context


class HTTPRedirectHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that redirects all requests to HTTPS."""
    def do_GET(self):
        self.send_redirect()

    def do_POST(self):
        self.send_redirect()

    def do_HEAD(self):
        self.send_redirect()

    def send_redirect(self):
        host = self.headers.get("Host", "").split(":")[0]
        if not host:
            host = "localhost"
        target_url = f"https://{host}{self.path}"
        self.send_response(301)
        self.send_header("Location", target_url)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP redirect log spam


def start_http_redirect_server(port=80):
    """Run an HTTP-to-HTTPS redirect server on a background thread."""
    try:
        server = HTTPServer(("0.0.0.0", port), HTTPRedirectHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f" * HTTP redirect server running on port {port} -> HTTPS (port 443)")
    except Exception as e:
        print(f" * Could not start HTTP redirect server on port {port}: {e}")


app = create_app()

if __name__ == "__main__":
    certfile = None
    keyfile = None
    with app.app_context():
        ssl_ctx = get_ssl_context()
        if ssl_ctx:
            certfile, keyfile = ssl_ctx

    if certfile and keyfile:
        # HTTPS mode: SocketIO on port 443 (or HTTPS_PORT), HTTP redirect on port 80 (or HTTP_PORT)
        https_port = Config.HTTPS_PORT
        http_port = Config.HTTP_PORT
        start_http_redirect_server(port=http_port)

        run_kwargs = {
            "host": "0.0.0.0",
            "port": https_port,
            "debug": True,
            "allow_unsafe_werkzeug": True,
            "certfile": certfile,
            "keyfile": keyfile
        }
        app.logger.info("Starting server in HTTPS mode on port %d (HTTP redirect on port %d)", https_port, http_port)
    else:
        # HTTP mode: SocketIO on port 80 (or HTTP_PORT)
        http_port = Config.HTTP_PORT
        run_kwargs = {
            "host": "0.0.0.0",
            "port": http_port,
            "debug": True,
            "allow_unsafe_werkzeug": True
        }
        app.logger.info("Starting server in HTTP mode on port %d", http_port)

    socketio.run(app, **run_kwargs)
