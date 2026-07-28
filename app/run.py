import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*eventlet.*")
warnings.filterwarnings("ignore", message=".*Eventlet is deprecated.*")

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
        try:
            from app.utils import get_setting
            with app.app_context():
                ssl_enabled = get_setting("ssl_enabled", "false") == "true"
        except Exception:
            ssl_enabled = True

        if not ssl_enabled:
            # SSL was disabled/deleted in DB! Stop redirecting to HTTPS!
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<title>HTTP — Restart Required</title>"
                "<style>body{font-family:sans-serif;text-align:center;padding:3rem;background:#f8fafc;color:#0f172a;}"
                ".card{max-width:520px;margin:auto;background:white;padding:2rem;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1);}"
                "code{background:#f1f5f9;padding:0.6rem;display:block;border-radius:8px;margin:1rem 0;font-size:0.95rem;color:#0f172a;}"
                "</style></head><body><div class='card'>"
                "<h2>🔓 SSL-Zertifikat gelöscht (HTTP aktiv)</h2>"
                "<p>Das Zertifikat wurde entfernt und der Server auf HTTP zurückgesetzt.</p>"
                "<p><strong>Bitte starte den Docker-Container neu</strong>, damit der Server den Port 80 im HTTP-Modus bindet:</p>"
                "<code>docker compose down && docker compose up -d</code>"
                "</div></body></html>"
            )
            self.wfile.write(html.encode("utf-8"))
            return

        host = self.headers.get("Host", "").split(":")[0]
        if not host:
            host = "localhost"
        target_url = f"https://{host}{self.path}"
        self.send_response(302)  # Temporary redirect so browser does not cache permanently
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

        is_dev = app.config.get("DEV_MODE", False)
        run_kwargs = {
            "host": "0.0.0.0",
            "port": https_port,
            "debug": is_dev,
            "allow_unsafe_werkzeug": is_dev,
            "certfile": certfile,
            "keyfile": keyfile
        }
        app.logger.info("Starting server in HTTPS mode on port %d (HTTP redirect on port %d, dev_mode=%s)", https_port, http_port, is_dev)
    else:
        # HTTP mode: SocketIO on port 80 (or HTTP_PORT)
        http_port = Config.HTTP_PORT
        is_dev = app.config.get("DEV_MODE", False)
        run_kwargs = {
            "host": "0.0.0.0",
            "port": http_port,
            "debug": is_dev,
            "allow_unsafe_werkzeug": is_dev
        }
        app.logger.info("Starting server in HTTP mode on port %d (dev_mode=%s)", http_port, is_dev)

    socketio.run(app, **run_kwargs)
