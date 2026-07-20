import os
import logging
from flask import Flask
from app.config import Config
from app.db import db
from app.seed import seed_default_products
from app.services.socket_events import socketio, register_socket_events
from app.routes.cashier import cashier_bp
from app.routes.admin import admin_bp
from app.routes.api import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist
    os.makedirs(os.path.join(app.root_path, "data"), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "static", "images", "products"), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "static", "images", "cards"), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    app.register_blueprint(cashier_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register socket event handlers
    register_socket_events(socketio)

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_default_products()

    logger.info("Kinder-Supermarkt app initialized successfully.")
    return app
