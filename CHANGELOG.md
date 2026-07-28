# Changelog

Alle wesentlichen Änderungen an **Kinder-Supermarkt** werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).
Versionierung nach [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-07-28

> 🎉 **Erstes stabiles Release**

### ✨ Hinzugefügt

#### Kassen-Tablet (Landscape PWA)
- Kind-gerechte Produktkacheln mit Emoji oder Foto, Kategorien-Seitenleiste, Pagination ohne Scrollen
- Echtzeit-Warenkorb, Summe, Mengen-Buttons
- Web Audio API Sounds: Scan-Piep, Fanfare, Fehlerbuzz
- Vollbild-Zahlungsoverlay mit Kundenphoto, Unterschrift und 8-s-Countdown
- Landscape-Enforcement mit Warn-Overlay
- NFC-Scanner-Banner (Hand-Scanner Modus)
- Installierbar als PWA (`manifest.json`)

#### Terminal-Smartphone (Portrait PWA)
- Web NFC via `window.NDEFReader` (Android Chrome)
- Touchscreen-Kartenwahl (iOS / Fallback)
- Dauerhafte NFC-Berechtigung via `localStorage`
- 4 Zahlungsmodi: Direkt / Spielgeld-PIN / Exakter PIN / Unterschrift-Canvas
- Hand-Scanner-Modus: NFC-Produkt-Tags im Leerlauf scannen → Artikel direkt in Tablet-Warenkorb
- Konfigurierbarer Standby-Timeout
- Installierbar als PWA (`manifest-terminal.json`)

#### Bon-System
- Visueller Drag & Drop Bon-Builder (Blöcke: Shop-Name, Text, Trennlinie, Metadaten, Kunde, Artikel, Unterschrift, QR-Code)
- Live-Vorschau (thermopapier-genau) im Admin
- PDF-Bon im Browser (`/receipt/<id>`)
- Muster-Bon zum Testen (`/receipt/preview`)
- USB-Thermodrucker via `python-escpos`
- Papierformat 58 mm / 80 mm
- Druckmodus: Immer / Nachfragen / Nie + Rate-Limit

#### Admin-Panel (`/admin`)
- Touchscreen-PIN-Pad (Standard: `1234`)
- Dashboard: KPI-Kacheln, 7-Tage-Umsatzchart, Top-Produkte, Top-Kunden, letzte Transaktionen
- Produkt-CRUD: Bild, Emoji-Picker, Preis, Kategorie, NFC-UID (live scannen)
- Kategorie-CRUD: Emoji-Picker, Sortierung, Aktiv/Inaktiv
- Karten-CRUD: NFC-Registrierung per Tap, Foto, PIN
- Transaktionshistorie mit Einzellöschung und Reset
- Einstellungen: Shop-Name, PIN, NFC-Modus, Hand-Scanner, Timeout, Debug, Bon-Builder, Drucker
- SSL/HTTPS-Verwaltung direkt im Browser (Zertifikat, Key, CA-Kette hochladen)
- Installierbar als PWA (`manifest-admin.json`)

#### Backend & Infrastruktur
- Flask + Flask-SocketIO WebSocket-Kommunikation (Tablet ↔ Terminal)
- SQLite via SQLAlchemy, automatische Schema-Migrationen beim Start
- Docker Compose Single-Container auf Port 80/443
- PWA Service Worker: Cache-First für Static Assets
- Offline-First: kein Internet nötig
- Lokaler QR-Code-Generator (`qrcode`-Library, kein externer Dienst)

#### REST API
- `GET /api/health`, `/api/products`, `/api/cards`, `/api/products/by_nfc/<uid>`
- `GET/POST /api/nfc_tap` — Webhook für externe Automatisierung
- `POST /api/print_receipt/<tx_id>` — Thermodruck per API

#### Dev-Simulator
- 🧪-Drawer auf der Kassenseite (nur bei `DEV_MODE=true`)
- Schnell-Testkarten, Custom NFC-UID, PIN-Simulation, Schnelllinks

---

### 🐛 Bug-Fixes

| ID | Datei | Beschreibung |
|---|---|---|
| BUG-1 | `base_admin.html` / `admin.js` | `copyToClipboard` `ReferenceError` auf allen Admin-Seiten außer Settings behoben |
| BUG-2 | `terminal.html` | `activePayState` undefiniert im `payment_error`-Handler — Variable korrekt deklariert |
| BUG-3 | `products.html`, `categories.html`, `cards.html` | JS-Syntaxfehler bei Namen mit Apostroph — `data-*`-Attribute statt Inline-String-Interpolation |
| BUG-4 | `admin.js` | Externer QR-API-Aufruf (`api.qrserver.com`) im Bon-Builder entfernt (Offline-Verletzung) |
| BUG-5 | `printer.py`, `seed.py` | `Model.query.get()` → `db.session.get()` (SQLAlchemy 2.x deprecated) |
| BUG-6 | `run.py` | `debug=True` + `allow_unsafe_werkzeug=True` in Production entfernt |
| BUG-7 | `admin.py` | CSRF: DELETE-Routen von GET auf POST umgestellt |
| BUG-8 | `qr_generator.py` | Fallback auf externen API-Dienst entfernt |
| BUG-9 | `socket_events.py` | NFC-Tap lud alle Karten per `Card.query.all()` — ersetzt durch indexierten SQL-Filter |
| UX-3 | `dashboard.html` | Währungsformat: `"0,0€"` → `"0,00 €"` |
| UX-5 | `receipt.html` | Zurück-Button: `javascript:history.back()` → Fallback auf `/` wenn kein History |
| UX-8 | `cards.html` | Karten-PINs im Klartext → `••••` |
| UX-9 | `receipt.html`, `printer.py` | `show_date_time` / `show_card_name` parallel-System entfernt — Block-`enabled` ist alleinige Steuerung |

---

### ♻️ Verbesserungen

- **NFC-Lookup**: O(1) statt O(n) — indexierter SQL-Lookup mit normalisiertem Fallback
- **Emoji-Picker Kategorien**: Add- und Edit-Modal jetzt mit Emoji-Picker-Grid (analog Produkte)
- **Service Worker**: `admin.js` in Precache aufgenommen, Version auf `1.0.0`
- **Hardcoded Fallback-Kategorien** aus `cashier.html` entfernt — DB-Seed läuft immer beim Start
- **`.gitignore`**: SSL-Zertifikate (`*.pem`, `*.key`, `*.crt`), `debug/`, User-Uploads, `.pytest_cache`
- **`/debug`**: Development-Screenshots aus Repository entfernt
- **`docs/`**: `CHECKLIST.md` (Dev-Artefakt) entfernt; `DEV_MODE.md` als Feature-Doku überarbeitet
- **README**: Komplett neu — klare Projektübersicht ohne Dev-Rauschen
- **setup.md**: Komplett neu — vollständige Anleitung inkl. Docker-Drucker-Config, HTTPS, Erstkonfiguration, Env-Vars

---

### 📦 Abhängigkeiten (v1.0.0)

| Paket | Version |
|---|---|
| Flask | ≥3.1.3 |
| Flask-SocketIO | ≥5.5.1 |
| Flask-SQLAlchemy | ≥3.1.1 |
| Werkzeug | ≥3.1.8 |
| python-escpos | ≥3.1 |
| Pillow | ≥11.2.1 |
| qrcode | ≥8.1 |
| eventlet | ≥0.41.1 |
| cryptography | ≥45.0.3 |
| python-dotenv | ≥1.1.1 |

---

[1.0.0]: https://github.com/Ayakashi97/kids-supermarket/releases/tag/v1.0.0
