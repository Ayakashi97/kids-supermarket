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
- **Database**: SQLite via SQLAlchemy (for products, categories, transactions, customer cards, settings)
- **Orientation**: Terminal locked to **Portrait** (`portrait`); Cashier UI locked to **Landscape** (`landscape`) with kid-friendly **Pagination** (no scrolling)
- **Printer**: Epson TM-series USB thermal receipt printer (via `python-escpos`) + Printable PDF Exporter
- **NFC Reader**: Smartphone Web NFC API (`window.NDEFReader` on Android Chrome with `localStorage` activation persistence) OR Touchscreen Card Selector (iOS Safari / Fallback) OR optional PN532 hardware
- **PWA**: Dual Web App Manifests (`manifest.json` for Cashier App, `manifest-terminal.json` for Terminal App) + Service Worker (`sw.js`) for full-screen "Add to Home Screen" on iOS & Android
- **Containerization**: Docker + Docker Compose (multi-service)
- **Configuration**: Dynamic Shop Name (`shop_name`), categories, card photos, receipt layouts, and settings via admin panel (stored in SQLite)

## Hardware Architecture
```
[Tablet / Browser (Cashier)] <──HTTP/WebSocket──> [Raspberry Pi #1: Backend Server] <──HTTP/WebSocket──> [Smartphone (Terminal PWA + Web NFC)]
                                                            │
                                                  [USB Thermal Printer]
```

- **Raspberry Pi #1**: Runs the Flask backend + Docker Compose stack (Port `5050` or `5000`)
- **Tablet**: Browser pointing to `http://<pi1-ip>:5050` — acts as the cashier display in landscape mode with pagination system (Installable PWA "Supermarkt Kasse")
- **Smartphone (Android / iPhone)**: Opens `http://<pi1-ip>:5050/terminal` in portrait mode as a PWA (Installable PWA "Supermarkt Terminal").
  On Android Chrome, it reads NFC cards directly via built-in Web NFC (`NDEFReader`). On iOS / non-WebNFC devices, it acts as an interactive touchscreen terminal with card selection buttons and full-screen animations.
- **USB Thermal Printer**: Connected to Raspberry Pi #1 via USB

## Key Rules & Conventions
- **Kid-friendly UI first**: Big buttons, bright colors, large emoji/icons, simple animations
- **No small text**: Minimum font size 18px everywhere in the cashier UI
- **No scrolling for kids on Cashier UI**: Fixed height/width with large `◀ ZURÜCK` / `WEITER ▶` pagination arrows
- **Orientation Enforcement**: Terminal is locked to Portrait mode; Cashier is locked to Landscape mode. Warning overlays appear if device orientation is incorrect
- **Dynamic Categories**: Admin can add, edit, toggle, and delete categories with custom emojis and sort orders
- **Dynamic Naming**: The supermarket name (`shop_name`) is dynamically fetched from settings and rendered across Cashier, Terminal, Receipts, Admin, and page titles
- **Safe Area Spacing**: Top and bottom breathable margins/padding (`env(safe-area-inset-top)` / `env(safe-area-inset-bottom)`) so no UI element is cut off by camera notches or screen edges
- **Sounds**: Use browser Web Audio API for synthesized feedback sounds (success fanfare, item add beep, error buzz)
- **Admin panel** is at `/admin` — mobile-first responsive design, protected by a touchscreen **PIN-Pad** (default: `1234`)
- **All monetary values** are stored as integers (cents), displayed formatted (e.g. `1,50 €`)
- **Receipts**: Printed in German via USB ESC/POS thermal printer + exported/viewed as PDF (`/receipt/<tx_id>`)
- **Error handling**: All errors shown in a friendly, large, colorful dialog — never raw tracebacks
- **Offline-first**: The system must work without internet access
- **No TypeScript, no React, no Node.js** — plain Python + HTML/CSS/JS only

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
│   ├── models.py              ← SQLAlchemy models (Product, Category, Card, Transaction, TransactionItem, Setting)
│   ├── db.py                  ← DB init & helpers
│   ├── seed.py                ← Initial products, categories & test cards seeding
│   ├── routes/
│   │   ├── cashier.py         ← Cashier UI, PDF receipt, PWA manifests & SW routes
│   │   ├── admin.py           ← Admin panel routes & category management
│   │   └── api.py             ← REST API & /api/nfc_tap webhook
│   ├── services/
│   │   ├── printer.py         ← Receipt printing via python-escpos
│   │   └── socket_events.py   ← Flask-SocketIO event handlers (Web NFC & card lookup)
│   ├── static/
│   │   ├── manifest.json          ← PWA Manifest for Cashier App (Landscape)
│   │   ├── manifest-terminal.json ← PWA Manifest for Terminal App (Portrait)
│   │   ├── sw.js                  ← PWA Service Worker
│   │   ├── css/
│   │   │   ├── main.css       ← Cashier UI & Terminal styles
│   │   │   └── admin.css      ← Mobile-first Admin panel & PIN-Pad styles
│   │   ├── js/
│   │   │   ├── cashier.js     ← Cart logic, Pagination system, Web Audio API, WebSocket client
│   │   │   └── admin.js       ← Admin CRUD logic
│   │   └── images/
│   │       ├── favicon.png    ← Favicon icon
│   │       ├── favicon.ico    ← Favicon icon
│   │       ├── gen_icons.py   ← Favicon generator script
│   │       ├── products/      ← Product images
│   │       └── cards/         ← Customer card photos
│   └── templates/
│       ├── base.html          ← Base layout with PWA meta tags, Favicons & Service Worker
│       ├── cashier.html       ← Dynamic cashier view with pagination & landscape lock
│       ├── terminal.html      ← Glassmorphic Smartphone Web NFC & Touchscreen Terminal UI (Portrait)
│       ├── receipt.html       ← Thermal receipt & PDF export view
│       └── admin/
│           ├── login.html     ← Touchscreen PIN-Pad login
│           ├── dashboard.html
│           ├── categories.html← Dynamic category CRUD management
│           ├── products.html
│           ├── cards.html     ← NFC card registration (Smartphone Web NFC + socket)
│           ├── settings.html  ← Receipt layout & shop settings (NFC mode chooser)
│           └── transactions.html
├── nfc_reader/                ← Optional standalone PN532 daemon for Pi #2 (Legacy)
└── docs/
    ├── setup.md               ← Complete Raspberry Pi OS & Smartphone setup guide
    ├── DEV_MODE.md            ← Dev emulation & PDF testing guide
    ├── CHECKLIST.md           ← Master phase checklist
    └── PHASE_1.md - PHASE_9.md
```
