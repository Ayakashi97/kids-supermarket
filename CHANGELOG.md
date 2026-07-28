# Changelog

Alle wesentlichen Änderungen an **Kinder-Supermarkt** werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).
Versionierung nach [Semantic Versioning](https://semver.org/).

## [1.0.1] — 2026-07-28

### 🐛 Behoben

#### Terminal-Smartphone & NFC-Anlernen
- **Modus-Wechsel im Scan-Modus**: Das Terminal wechselt beim Starten einer Tag- oder Kundenkarten-Erfassung im Admin-Bereich jetzt automatisch in den visuellen **Scan-Modus** (mit dynamischem Titel, Untertitel und animiertem Halo-Ring 💳 / 🏷️).
- **Vollbild-Verschachtelung korrigiert**: Das `<div id="stateRegistration">` lag fälschlicherweise innerhalb von `stateScannerIdle`, wodurch der Bildschirm beim Anlernen schwarz blieb. Das Element wurde entverschachtelt.
- **Kundenkarten-Erfassung im Admin**: `cards.html` hörte bisher nur auf das Event `card_tapped` anstelle von `card_captured`. Das Event wurde hinzugefügt, sodass gescannte UIDs sofort im Kundenkarten-Formular eingefügt werden.
- **Abbrechen-Handler**: Das Schließen der Admin-Modals sendet jetzt ein `cancel_registration`-Event, damit das Terminal direkt zum Leerlauf-Bildschirm zurückkehrt.
- **Hilfetext im Admin**: Hilfetext unter dem NFC-UID-Feld in der Kundenkarten-Registrierung hinzugefügt.

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

[1.0.1]: https://github.com/Ayakashi97/kids-supermarket/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Ayakashi97/kids-supermarket/releases/tag/v1.0.0
