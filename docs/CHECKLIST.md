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
- [x] Implement Flask-SocketIO event handlers (`start_payment`, `card_tapped`, `payment_success`, `payment_error`, `card_registered`)
- [x] Server maintains state machine: `idle` / `waiting_for_payment` / `waiting_for_registration`
- [x] NFC card lookup in `Card` table (known card → greeting + photo; unknown card → error)
- [x] Fullscreen overlay "Karte hinhalten! 💳" with pulsing animation
- [x] Success overlay with card holder photo + "Hallo [Name]! 🎉"
- [x] Save transaction to DB (Transaction + TransactionItems linked to Card)

## Phase 4 — Receipt Printing
- [x] ESC/POS USB thermal printer service implementation (`python-escpos`)
- [x] Format receipt in German (Shop name, date, time, card holder name, items, total, thank-you message)
- [x] Dynamic admin settings support (`printer_enabled`, `printer_device`, `shop_name`, `receipt_header`, `receipt_footer`, `paper_width`, `show_card_name`, `show_date_time`)
- [x] PDF & Printable Web Receipt generator (`/receipt/<tx_id>` & `/receipt/preview`)
- [x] Device passthrough via Docker (`/dev/usb/lp0`)
- [x] Fallback logging if printer disconnected

## Phase 5 — NFC Reader Service & Touchscreen Terminal (Pi #2)
- [x] Dedicated terminal route `/terminal` for Pi #2 touchscreen (browser kiosk mode)
- [x] Real-time payment animations on Pi #2 display (waiting pulse, card tapping animation, success photo overlay)
- [x] Standalone Python script `nfc_reader/reader.py`
- [x] PN532 module connection (SPI/I2C via `nfcpy`/`pn532`)
- [x] Connect to Pi #1 Flask-SocketIO server and emit `card_tapped`
- [x] Rate-limit repeated taps (3s debounce)
- [x] Systemd service script for Pi #2 auto-start

## Phase 6 — Admin Panel
- [x] Touchscreen PIN-Pad admin login `/admin/login`
- [x] Dashboard stats (products count, cards count, total transactions, play money total)
- [x] Product CRUD (name, price in cents, category, emoji/image upload)
- [x] Card Management (`/admin/cards`): register new card by NFC tap, name, photo upload, toggle active, delete
- [x] Settings UI (`/admin/settings`): Shop name, admin PIN, printer enable toggle, device path, paper width, header & footer customization, show/hide card name
- [x] Transaction history viewer (`/admin/transactions`) with PDF export links

## Phase 7 — Polish & Kid Experience
- [x] Development & Emulation Testing Mode (`DEV_MODE=true`, floating NFC simulator bar, test card seeding)
- [x] Audio feedback (beep, success, error sounds synthesized via Web Audio API)
- [x] Product category navigation tabs
- [x] Scanning animations
- [x] Touch-optimized UI elements (minimum 80px tap targets)

## Phase 8 — Smartphone Web NFC, Dual PWA & Dynamic Customization
- [x] Replaced Pi #2 requirement with Smartphone (Android / iPhone)
- [x] Web NFC API integration (`window.NDEFReader`) in `/terminal` for Android Chrome
- [x] Persistent NFC permission state (`localStorage.setItem("nfc_permission_granted", "true")`)
- [x] Dual Progressive Web App (PWA) manifests (`manifest.json` for Cashier, `manifest-terminal.json` for Terminal) & Service Worker (`sw.js`)
- [x] Borderless fullscreen app mode for iOS Safari & Android Chrome ("Add to Home Screen")
- [x] Favicon generation (`favicon.png`, `favicon.ico`, `apple-touch-icon.png`) and base template linking
- [x] Flexible NFC UID normalization (`find_card_by_uid`) in backend socket events
- [x] Web NFC card scanning in Admin Card Registration (`/admin/cards`)
- [x] Dynamic Shop Name (`shop_name`) customization across Cashier UI, Terminal UI, Receipts, Admin, and page titles
- **[x]** Responsive layout bounds & safe area spacing (`env(safe-area-inset-top)` / `env(safe-area-inset-bottom)`) preventing cut-off UI elements

## Phase 9 — Orientation Locking, Cashier Pagination, Mobile-First Admin & Dynamic Categories
- [x] Locked Terminal UI to **Portrait** mode (`manifest-terminal.json` orientation + `screen.orientation.lock('portrait')` + landscape warning overlay)
- [x] Locked Cashier UI to **Landscape** mode (`manifest.json` orientation + `screen.orientation.lock('landscape')` + portrait warning overlay)
- [x] Kid-Friendly Cashier **Pagination system** with large `◀ ZURÜCK` / `WEITER ▶` arrow buttons (eliminating scrolling for kids)
- [x] Dynamic calculation of `itemsPerPage` based on container dimensions
- [x] Dynamic `Category` database model (`Category` table with `name`, `emoji`, `sort_order`, `is_active`)
- [x] Dynamic category seeding & cashier tabs rendering from database
- [x] Mobile-First Admin Panel Redesign (`admin.css` rewrite with hamburger menu `☰`, touch targets ≥48px, font size ≥18px, responsive card & table views)
- [x] Admin Category Management (`/admin/categories`) with add, toggle, delete, sort order, and emoji support
- [x] Dynamic category select dropdown in Admin Product Management (`/admin/products`)

