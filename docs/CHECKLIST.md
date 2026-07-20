# 📋 Kinder-Supermarkt Project Master Checklist

## Phase 1 — Foundation & Project Scaffold
- [x] Initialize project directory structure
- [x] Create `docker-compose.yml` with `web` service
- [x] Create `app/Dockerfile` (Python 3.11 slim)
- [x] Set up Flask app factory (`app/__init__.py`)
- [x] Configure Flask-SocketIO
- [x] Set up SQLAlchemy + SQLite
- [x] Define data models (`Product`, `Card`, `Transaction`, `TransactionItem`, `Setting`)
- [x] Create `.env.example` and `.gitignore`
- [x] Seed default German products on first run

## Phase 2 — Cashier UI (Tablet Frontend)
- [x] Design and implement `cashier.html` with product grid + cart panel
- [x] Kid-friendly CSS (big rounded buttons, bright colors, large emojis)
- [x] Implement `cashier.js`: add item to cart, update totals, remove items
- [x] Add "beep" sound on item add (Web Audio API)
- [x] Cart shows: item list, quantities, individual prices, total
- [x] "Bezahlen 💳" button — triggers payment flow
- [x] "Warenkorb leeren 🗑️" button — clears cart with confirmation

## Phase 3 — Payment Flow (WebSocket)
- [ ] Implement Flask-SocketIO event handlers (`start_payment`, `card_tapped`, `payment_success`, `payment_error`, `card_registered`)
- [ ] Server maintains state machine: `idle` / `waiting_for_payment` / `waiting_for_registration`
- [ ] NFC card lookup in `Card` table (known card → greeting + photo; unknown card → error)
- [ ] Fullscreen overlay "Karte hinhalten! 💳" with pulsing animation
- [ ] Success overlay with card holder photo + "Hallo [Name]! 🎉"
- [ ] Save transaction to DB (Transaction + TransactionItems linked to Card)

## Phase 4 — Receipt Printing
- [ ] ESC/POS USB thermal printer service implementation (`python-escpos`)
- [ ] Format receipt in German (Shop name, date, time, card holder name, items, total, thank you message)
- [ ] Device passthrough via Docker (`/dev/usb/lp0`)
- [ ] Fallback logging if printer disconnected

## Phase 5 — NFC Reader Service & Touchscreen Terminal (Pi #2)
- [ ] Dedicated terminal route `/terminal` for Pi #2 touchscreen (browser kiosk mode)
- [ ] Real-time payment animations on Pi #2 display (waiting pulse, card tapping animation, success photo overlay)
- [ ] Standalone Python script `nfc_reader/reader.py`
- [ ] PN532 module connection (SPI/I2C via `nfcpy`/`pn532`)
- [ ] Connect to Pi #1 Flask-SocketIO server and emit `card_tapped`
- [ ] Rate-limit repeated taps
- [ ] Systemd service script for Pi #2 auto-start

## Phase 6 — Admin Panel
- [ ] Admin login `/admin` with PIN authentication
- [ ] Dashboard stats (products count, cards count, total transactions)
- [ ] Product CRUD (name, price in cents, category, emoji/image upload)
- [ ] Card Management (`/admin/cards`): register new card by NFC tap, name, photo upload, toggle active, delete
- [ ] Transaction history viewer

## Phase 7 — Polish & Kid Experience
- [ ] Audio feedback (beep, success, error sounds)
- [ ] Product category navigation tabs
- [ ] Scanning animations
- [ ] Touch-optimized UI elements (minimum 80px tap targets)
