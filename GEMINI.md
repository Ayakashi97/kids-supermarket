# Kinder-Supermarkt (Kids Supermarket Play System)

## Project Overview
A play supermarket system designed for children aged 3+.
It consists of a tablet-based cashier UI (Flask web app), a single Raspberry Pi backend server (Pi #1),
and an old smartphone (Android/iPhone) acting as the NFC card reader terminal and display via Web NFC & PWA mode.

## Language
- UI language: **German** (all product names, buttons, messages in German)
- Code language: **English** (variables, functions, comments)

## Tech Stack
- **Backend**: Python 3.11+, Flask, Flask-SocketIO
- **Frontend**: HTML + Vanilla CSS + Vanilla JS (no frameworks)
- **Communication**: WebSockets (Flask-SocketIO) for real-time updates between tablet and smartphone terminal
- **Database**: SQLite via SQLAlchemy (for products, transactions, customer cards, settings)
- **Printer**: Epson TM-series USB thermal receipt printer (via `python-escpos`) + Printable PDF Exporter
- **NFC Reader**: Smartphone Web NFC API (`window.NDEFReader` on Android Chrome) OR Touchscreen Card Selector (iOS Safari / Fallback) OR optional PN532 hardware
- **PWA**: Web App Manifest (`manifest.json`) + Service Worker (`sw.js`) for full-screen "Add to Home Screen" on iOS & Android
- **Containerization**: Docker + Docker Compose (multi-service)
- **Configuration**: Products, card photos, receipt layouts, and settings via admin panel (stored in SQLite)

## Hardware Architecture
```
[Tablet / Browser (Cashier)] <──HTTP/WebSocket──> [Raspberry Pi #1: Backend Server] <──HTTP/WebSocket──> [Smartphone (Terminal PWA + Web NFC)]
                                                            │
                                                  [USB Thermal Printer]
```

- **Raspberry Pi #1**: Runs the Flask backend + Docker Compose stack (Port `5050` or `5000`)
- **Tablet**: Browser pointing to `http://<pi1-ip>:5050` — acts as the cashier display
- **Smartphone (Android / iPhone)**: Opens `http://<pi1-ip>:5050/terminal` as a PWA (full-screen App).
  On Android Chrome, it reads NFC cards directly via built-in Web NFC (`NDEFReader`). On iOS / non-WebNFC devices, it acts as an interactive touchscreen terminal with card selection buttons and full-screen animations.
- **USB Thermal Printer**: Connected to Raspberry Pi #1 via USB

## Services (Docker Compose on Pi #1)
| Service | Description |
|---|---|
| `web` | Flask app (cashier UI + REST API + WebSocket server + PDF receipt engine + Admin Panel + PWA manifest & SW) |

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
│   │   ├── cashier.py         ← Cashier UI, PDF receipt & PWA routes
│   │   ├── admin.py           ← Admin panel routes
│   │   └── api.py             ← REST API
│   ├── services/
│   │   ├── printer.py         ← Receipt printing via python-escpos
│   │   └── socket_events.py   ← Flask-SocketIO event handlers (Web NFC & card lookup)
│   ├── static/
│   │   ├── manifest.json      ← PWA Web App Manifest
│   │   ├── sw.js              ← PWA Service Worker
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
│       ├── base.html          ← Base layout with PWA meta tags & Service Worker
│       ├── cashier.html       ← Main cashier view
│       ├── terminal.html      ← Smartphone Web NFC & Touchscreen Terminal UI
│       ├── receipt.html       ← Thermal receipt & PDF export view
│       └── admin/
│           ├── login.html     ← Touchscreen PIN-Pad login
│           ├── dashboard.html
│           ├── products.html
│           ├── cards.html     ← NFC card registration (Smartphone Web NFC + socket)
│           ├── settings.html  ← Receipt layout & shop settings (NFC mode chooser)
│           └── transactions.html
├── nfc_reader/                ← Optional standalone PN532 daemon for Pi #2 (Legacy)
│   ├── requirements.txt
│   ├── reader.py
│   └── README.md
└── docs/
    ├── setup.md               ← Complete Raspberry Pi OS & Smartphone setup guide
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
- [x] **Phase 5: NFC Reader Service & Touchscreen Terminal (Pi #2 / Smartphone Web NFC)**
- [x] **Phase 6: Admin Panel (PIN-Pad Login, Product & Card Management, Editable Receipt Settings)**
- [x] **Phase 7: Polish & Kid Experience (DEV_MODE emulation bar, PDF toolbar link, Web Audio API)**
- [x] **Phase 8: Smartphone Web NFC & PWA Migration (Replaced Pi #2 with Android/iPhone PWA)**
