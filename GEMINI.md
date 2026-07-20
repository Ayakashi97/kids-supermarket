# Kinder-Supermarkt (Kids Supermarket Play System)

## Project Overview
A play supermarket system designed for children aged 3+.
It consists of a tablet-based cashier UI (Flask web app), a Raspberry Pi backend server,
and a second Raspberry Pi acting as the NFC card reader terminal.

## Language
- UI language: **German** (all product names, buttons, messages in German)
- Code language: **English** (variables, functions, comments)

## Tech Stack
- **Backend**: Python 3.11+, Flask, Flask-SocketIO
- **Frontend**: HTML + Vanilla CSS + Vanilla JS (no frameworks)
- **Communication**: WebSockets (Flask-SocketIO) for real-time updates between tablet and NFC reader
- **Database**: SQLite via SQLAlchemy (for products, transactions)
- **Printer**: Epson TM-series USB thermal receipt printer (via `python-escpos`)
- **NFC Reader**: PN532 via SPI/I2C on second Raspberry Pi (via `nfcpy` or `pn532` library)
- **Containerization**: Docker + Docker Compose (multi-service)
- **Configuration**: Products and settings via admin panel (stored in SQLite)

## Hardware Architecture
```
[Tablet / Browser]  <──HTTP/WebSocket──>  [Raspberry Pi #1: Backend Server]
                                                    │
                                          ┌─────────┴──────────┐
                                          │                    │
                               [USB Thermal Printer]  [Raspberry Pi #2: NFC Reader]
                                                              │
                                                      [PN532 NFC Module via SPI/I2C]
```

- **Raspberry Pi #1**: Runs the Flask backend + Docker Compose stack
- **Tablet**: Browser pointing to `http://<pi1-ip>:5000` — acts as the cashier display
- **Raspberry Pi #2**: Connected to PN532 NFC reader AND a touchscreen display.
  Opens `http://<pi1-ip>:5000/terminal` in kiosk mode to display real-time payment animations (pulsing card reader graphic, green checkmark, card holder photo), while running the Python NFC reader service.
- **USB Thermal Printer**: Connected to Raspberry Pi #1 via USB

## Services (Docker Compose on Pi #1)
| Service | Description |
|---|---|
| `web` | Flask app (cashier UI + REST API + WebSocket server) |

> Note: The SQLite DB is stored in a named Docker volume. The USB printer device is passed
> through to the container via `devices:` in docker-compose.yml.
> NFC reader on Pi #2 runs as a standalone Python script (not in Docker, needs GPIO access).
> It connects to the Flask WebSocket server on Pi #1.

## Key Rules & Conventions
- **Kid-friendly UI first**: Big buttons, bright colors, large emoji/icons, simple animations
- **No small text**: Minimum font size 18px everywhere in the cashier UI
- **Sounds**: Use browser Audio API for feedback sounds (success, beep on item add)
- **Admin panel** is at `/admin` — protected by a simple PIN (default: `1234`)
- **All monetary values** are stored as integers (cents), displayed formatted (e.g. `1,50 €`)
- **Receipts** are printed in German
- **Error handling**: All errors shown in a friendly, large, colorful dialog — never raw tracebacks
- **Offline-first**: The system must work without internet access
- **No TypeScript, no React, no Node.js** — plain Python + HTML/CSS/JS only
- **Docker**: All services use `restart: unless-stopped`
- **Environment**: Secrets and config via `.env` file (never committed)
- **Logging**: Structured logging to stdout (captured by Docker)

## File Structure
```
supermarket/
├── GEMINI.md                  ← You are here
├── PLAN.md                    ← Full architecture & implementation plan
├── docker-compose.yml
├── .env.example
├── .gitignore
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run.py                 ← Entry point
│   ├── config.py              ← Config from env vars
│   ├── models.py              ← SQLAlchemy models (Product, Transaction, TransactionItem, Card)
│   ├── db.py                  ← DB init & helpers
│   ├── routes/
│   │   ├── cashier.py         ← Cashier UI routes
│   │   ├── admin.py           ← Admin panel routes
│   │   └── api.py             ← REST API (used by NFC reader Pi)
│   ├── services/
│   │   ├── printer.py         ← Receipt printing via python-escpos
│   │   └── socket_events.py   ← Flask-SocketIO event handlers
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css       ← Cashier UI styles
│   │   │   └── admin.css      ← Admin panel styles
│   │   ├── js/
│   │   │   ├── cashier.js     ← Cart logic, WebSocket client
│   │   │   └── admin.js       ← Admin CRUD logic
│   │   ├── sounds/
│   │   │   ├── beep.mp3       ← Item added sound
│   │   │   ├── success.mp3    ← Payment success sound
│   │   │   └── error.mp3      ← Error sound
│   │   └── images/
│   │       ├── products/      ← Product images (emoji PNGs or uploaded images)
│   │       └── cards/         ← Customer card photos (uploaded via admin)
│   └── templates/
│       ├── base.html
│       ├── cashier.html       ← Main cashier view
│       ├── terminal.html      ← Pi #2 Touchscreen Terminal UI (card animations)
│       ├── admin/
│       │   ├── login.html
│       │   ├── dashboard.html
│       │   ├── products.html
│       │   └── cards.html     ← NFC card management (register, name, photo)
│       └── partials/
│           ├── product_grid.html
│           └── cart.html
├── nfc_reader/
│   ├── requirements.txt       ← nfcpy / pn532, python-socketio[client]
│   ├── reader.py              ← Polls NFC, sends WebSocket event to Pi #1
│   └── README.md
└── docs/
    └── setup.md               ← Hardware setup instructions
```

## Payment Flow
1. Tablet shows product grid → child taps items → cart builds up (with beep sound)
2. Child (or parent) taps "Bezahlen 💳" button → tablet shows "Karte hinhalten!" animation
3. Flask emits `waiting_for_payment` via WebSocket
4. NFC reader Pi polls PN532 → detects NFC sticker → reads UID
5. NFC reader sends `card_tapped` event with UID to Flask WebSocket server
6. Flask looks up the UID in the `Card` table:
   - **Known card** → emits `payment_success` with `{ name, image_url }` → tablet shows photo + "Hallo [Name]! 🎉"
   - **Unknown card** → emits `payment_error` with friendly message "Unbekannte Karte 😕"
7. Transaction is saved to DB (linked to Card if known)
8. Tablet plays success sound 🎉 + displays card holder's photo full-screen for ~3 seconds
9. Flask triggers receipt printing (card holder name printed on receipt)
10. Cart is cleared → system returns to product grid

## Card Registration Flow (Admin)
1. Parent opens `/admin/cards` → clicks "Neue Karte registrieren"
2. Admin panel shows "Bitte Karte jetzt hinhalten..." — server enters **registration mode**
3. NFC reader sends next `card_tapped` event → server captures the UID
4. Admin fills in: **Name** (e.g. "Lena"), uploads a **photo**
5. Card is saved to DB → immediately usable for payment

## Admin Panel Features (`/admin`)
- Add / edit / delete products (name, price in cents, emoji or uploaded image, category)
- **Card management** (`/admin/cards`):
  - Register new card by tapping it on the NFC reader → enter name + upload photo
  - Edit card name / photo
  - Delete card (unknown cards are then rejected at payment)
  - Toggle card active/inactive
- View transaction history (date, items, total, card holder name)
- Change admin PIN
- Toggle products active/inactive (hide without deleting)
- Set shop name (shown on receipt header)

## Coding Standards
- Python: Follow PEP8, use type hints where practical
- Use `logging` module, not `print()`
- Flask blueprints for route organization
- Keep templates clean — logic belongs in Python, not Jinja2
- CSS variables for all colors and spacing
- Responsive layout: tablet-first, minimum 768px wide
- Seed default products on first run (Brezel, Apfel, Banane, Milch, Käse, Brot, Saft, etc.)

## Phase Implementation Status & Documentation
Detailed documentation and progress checklists are maintained in the [`docs/`](file:///Users/jan/projects/supermarket/docs) directory:

- **[Phase 1 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_1.md)** — Foundation & Project Scaffold (COMPLETED)
- **[Phase 2 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_2.md)** — Cashier UI Tablet Frontend (COMPLETED)
- **[Phase 3 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_3.md)** — Payment Flow & Card Lookup (COMPLETED)
- **[Phase 4 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_4.md)** — Receipt Printing USB ESC/POS (COMPLETED)
- **[Phase 5 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_5.md)** — NFC Reader Service & Touchscreen Terminal (COMPLETED)
- **[Master Checklist](file:///Users/jan/projects/supermarket/docs/CHECKLIST.md)** — Overall project checklist per phase

### Phase Progress Summary
- [x] **Phase 1: Foundation & Project Scaffold** (Docker, Flask, SQLite, Models, Seed Data)
- [x] **Phase 2: Cashier UI (Tablet Frontend)** (Product grid, cart logic, Web Audio API sounds, category filtering)
- [x] **Phase 3: Payment Flow (WebSocket & Card Lookup)** (Server state machine, card DB lookup, transaction saving)
- [x] **Phase 4: Receipt Printing (USB ESC/POS)** (Thermal printer integration, admin configuration support)
- [x] **Phase 5: NFC Reader Service & Touchscreen Terminal (Pi #2)** (Touchscreen animations, PN532 polling service)
- [ ] **Phase 6: Admin Panel (Product & Card Management)**
- [ ] **Phase 7: Polish & Kid Experience**

