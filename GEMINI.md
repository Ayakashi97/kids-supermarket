# Kinder-Supermarkt (Kids Supermarket Play System)

## Project Overview
A play supermarket system designed for children aged 3+.
It consists of a tablet-based cashier UI (Flask web app), a Raspberry Pi backend server,
and a second Raspberry Pi acting as the NFC card reader terminal with touchscreen display animations.

## Language
- UI language: **German** (all product names, buttons, messages in German)
- Code language: **English** (variables, functions, comments)

## Tech Stack
- **Backend**: Python 3.11+, Flask, Flask-SocketIO
- **Frontend**: HTML + Vanilla CSS + Vanilla JS (no frameworks)
- **Communication**: WebSockets (Flask-SocketIO) for real-time updates between tablet and NFC reader
- **Database**: SQLite via SQLAlchemy (for products, transactions, customer cards, settings)
- **Printer**: Epson TM-series USB thermal receipt printer (via `python-escpos`) + Printable PDF Exporter
- **NFC Reader**: PN532 via SPI/I2C on second Raspberry Pi (via `nfcpy` or `adafruit-circuitpython-pn532`)
- **Containerization**: Docker + Docker Compose (multi-service)
- **Configuration**: Products, card photos, receipt layouts, and settings via admin panel (stored in SQLite)

## Hardware Architecture
```
[Tablet / Browser]  <──HTTP/WebSocket──>  [Raspberry Pi #1: Backend Server]
                                                    │
                                          ┌─────────┴──────────┐
                                          │                    │
                               [USB Thermal Printer]  [Raspberry Pi #2: NFC Reader]
                                                              │
                                                      [PN532 NFC Module + Touchscreen Display]
```

- **Raspberry Pi #1**: Runs the Flask backend + Docker Compose stack (Port `5050` or `5000`)
- **Tablet**: Browser pointing to `http://<pi1-ip>:5050` — acts as the cashier display
- **Raspberry Pi #2**: Connected to PN532 NFC reader AND a touchscreen display.
  Opens `http://<pi1-ip>:5050/terminal` in kiosk mode to display real-time payment animations (pulsing card reader graphic, green checkmark, card holder photo), while running the Python NFC reader service.
- **USB Thermal Printer**: Connected to Raspberry Pi #1 via USB

## Services (Docker Compose on Pi #1)
| Service | Description |
|---|---|
| `web` | Flask app (cashier UI + REST API + WebSocket server + PDF receipt engine + Admin Panel) |

> Note: The SQLite DB is stored in a named Docker volume. The USB printer device is passed
> through to the container via `devices:` in docker-compose.yml.
> NFC reader on Pi #2 runs as a standalone Python script (not in Docker, needs GPIO access).
> It connects to the Flask WebSocket server on Pi #1.

## Key Rules & Conventions
- **Kid-friendly UI first**: Big buttons, bright colors, large emoji/icons, simple animations
- **No small text**: Minimum font size 18px everywhere in the cashier UI
- **Sounds**: Use browser Web Audio API for synthesized feedback sounds (success fanfare, item add beep, error buzz)
- **Admin panel** is at `/admin` — protected by a touchscreen **PIN-Pad** (default: `1234`)
- **All monetary values** are stored as integers (cents), displayed formatted (e.g. `1,50 €`)
- **Receipts**: Printed in German via USB ESC/POS thermal printer + exported/viewed as PDF (`/receipt/<tx_id>`)
- **Error handling**: All errors shown in a friendly, large, colorful dialog — never raw tracebacks
- **Offline-first**: The system must work without internet access
- **No TypeScript, no React, no Node.js** — plain Python + HTML/CSS/JS only
- **Docker**: All services use `restart: unless-stopped`
- **Environment**: Secrets and config via `.env` file
- **Logging**: Structured logging to stdout

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
│   ├── models.py              ← SQLAlchemy models (Product, Transaction, TransactionItem, Card, Setting)
│   ├── db.py                  ← DB init & helpers
│   ├── seed.py                ← Initial products & test cards seeding
│   ├── routes/
│   │   ├── cashier.py         ← Cashier UI & PDF receipt routes
│   │   ├── admin.py           ← Admin panel routes
│   │   └── api.py             ← REST API
│   ├── services/
│   │   ├── printer.py         ← Receipt printing via python-escpos
│   │   └── socket_events.py   ← Flask-SocketIO event handlers
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css       ← Cashier UI & Terminal styles
│   │   │   └── admin.css      ← Admin panel & PIN-Pad styles
│   │   ├── js/
│   │   │   ├── cashier.js     ← Cart logic, Web Audio API, WebSocket client
│   │   │   └── admin.js       ← Admin CRUD logic
│   │   └── images/
│   │       ├── products/      ← Product images
│   │       └── cards/         ← Customer card photos
│   └── templates/
│       ├── base.html
│       ├── cashier.html       ← Main cashier view
│       ├── terminal.html      ← Pi #2 Touchscreen Terminal UI
│       ├── receipt.html       ← Thermal receipt & PDF export view
│       └── admin/
│           ├── login.html     ← Touchscreen PIN-Pad login
│           ├── dashboard.html
│           ├── products.html
│           ├── cards.html     ← NFC card registration
│           ├── settings.html  ← Receipt layout & shop settings
│           └── transactions.html
├── nfc_reader/
│   ├── requirements.txt       ← adafruit-circuitpython-pn532, python-socketio
│   ├── reader.py              ← Polls NFC, sends WebSocket event to Pi #1
│   └── README.md
└── docs/
    ├── setup.md               ← Complete Raspberry Pi OS & hardware guide
    ├── DEV_MODE.md            ← Dev emulation & PDF testing guide
    ├── CHECKLIST.md           ← Master phase checklist
    └── PHASE_1.md - PHASE_6.md
```

## Documentation Reference Directory
- **[Raspberry Pi Hardware & OS Setup Guide](file:///Users/jan/projects/supermarket/docs/setup.md)**
- **[Development & Emulation Mode Guide](file:///Users/jan/projects/supermarket/docs/DEV_MODE.md)**
- **[Master Phase Progress Checklist](file:///Users/jan/projects/supermarket/docs/CHECKLIST.md)**
- **[Phase 1 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_1.md)**
- **[Phase 2 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_2.md)**
- **[Phase 3 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_3.md)**
- **[Phase 4 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_4.md)**
- **[Phase 5 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_5.md)**
- **[Phase 6 Documentation](file:///Users/jan/projects/supermarket/docs/PHASE_6.md)**

### Phase Progress Summary
- [x] **Phase 1: Foundation & Project Scaffold**
- [x] **Phase 2: Cashier UI (Tablet Frontend)**
- [x] **Phase 3: Payment Flow (WebSocket & Card Lookup)**
- [x] **Phase 4: Receipt Printing & PDF Exporter (USB ESC/POS & PDF View)**
- [x] **Phase 5: NFC Reader Service & Touchscreen Terminal (Pi #2)**
- [x] **Phase 6: Admin Panel (PIN-Pad Login, Product & Card Management, Editable Receipt Settings)**
- [x] **Phase 7: Polish & Kid Experience (DEV_MODE emulation bar, PDF toolbar link, Web Audio API)**
