# Phase 1 Documentation — Foundation & Project Scaffold

## Summary of Completed Work
Phase 1 establishes the core infrastructure for the **Kinder-Supermarkt** application.

### Key Components Created:
1. **Containerization**:
   - `docker-compose.yml`: Defines the `web` service mapping port 5000, configuring volume mounts for persistent SQLite data (`db_data`) and static images, environment variables from `.env`, and USB device passthrough configuration for thermal printing.
   - `app/Dockerfile`: Uses `python:3.11-slim` with necessary native dependencies (`libusb-1.0-0-dev` for ESC/POS printing support).

2. **Backend Application Factory & Config**:
   - `app/config.py`: Loads configuration from `.env` (Secret key, DB URI, Shop name, Admin PIN, Printer device, Port).
   - `app/__init__.py`: Flask app factory setting up SQLite via SQLAlchemy, Flask-SocketIO, routing blueprints, database initialization, and automatic directory creation.
   - `app/run.py`: Server entry point running `socketio.run` on port 5000.

3. **Database & Models (`app/models.py`)**:
   - `Product`: Stores product details (name, `price_cents`, emoji, image path, category, active flag).
   - `Card`: Stores customer card info linked to NFC tags (`nfc_uid`, holder name, photo image path, active flag, timestamps).
   - `Transaction`: Stores sale transactions (`total_cents`, linked `card_id`, raw `nfc_uid`, status).
   - `TransactionItem`: Snapshot of individual items sold per transaction (`product_id`, `product_name`, `price_cents`, quantity).
   - `Setting`: Key-value store for app configuration.

4. **Default Product Seeding (`app/seed.py`)**:
   - Automatically seeds 12 default German products (Brezel, Apfel, Banane, Milch, Käse, Brot, Saft, Karotte, Schokolade, Eier, Muffin, Erdbeeren) on first run if DB is empty.

5. **Routes & Service Stubs**:
   - `app/routes/cashier.py`: Cashier blueprint rendering `cashier.html`.
   - `app/routes/admin.py`: Admin blueprint with PIN protection and dashboard routes.
   - `app/routes/api.py`: REST endpoints `/api/products`, `/api/cards`, `/api/health`.
   - `app/services/socket_events.py`: SocketIO handler scaffolding for payment and card registration state machine.
   - `app/services/printer.py`: Stub service for USB thermal printer integration via `python-escpos`.

6. **Frontend Base Templates**:
   - `app/templates/base.html`, `cashier.html`, `admin/login.html`, `admin/dashboard.html`.
   - `app/static/css/main.css`: Kid-friendly styling foundation (18px minimum font size, vibrant colors, rounded buttons).

---

## Phase 1 Checklist

- [x] Initialize project directory structure
- [x] Create `docker-compose.yml` with `web` service
- [x] Create `app/Dockerfile` (Python 3.11 slim)
- [x] Set up Flask app factory (`app/__init__.py`)
- [x] Configure Flask-SocketIO
- [x] Set up SQLAlchemy + SQLite
- [x] Define data models (`Product`, `Card`, `Transaction`, `TransactionItem`, `Setting`)
- [x] Create `.env.example` and `.gitignore`
- [x] Seed default German products on first run
