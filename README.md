# 🛒 Kinder-Supermarkt

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-SocketIO-000000.svg)](https://flask.palletsprojects.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

Ein vollständiges **Spiel-Supermarktsystem** für Kinder ab 3 Jahren — mit echter Tablet-Kasse, NFC-Zahlungsterminal auf einem alten Smartphone, USB-Thermodrucker und einem vollständigen Admin-Panel für Eltern.

---

## 📐 Hardware-Architektur

```
[Tablet (Kasse)] ◄──WebSocket──► [Raspberry Pi — Flask Server] ◄──WebSocket──► [Smartphone (Terminal + NFC)]
                                              │
                                   [USB Thermodrucker]
```

| Gerät | Rolle | App-Name |
|---|---|---|
| **Raspberry Pi** | Server (Flask, SQLite, Docker) | — |
| **Tablet** | Kassen-UI (Landscape PWA) | Supermarkt Kasse 🛒 |
| **Smartphone** | NFC-Terminal (Portrait PWA) | Supermarkt Terminal 💳 |

---

## ✨ Features

### 🛒 Kassen-Tablet (Landscape)
- Große, bunte Produktkacheln mit Emoji oder Foto, kategoriegefilterter Seitenleiste und Kind-gerechter Pagination (◀ ZURÜCK / WEITER ▶) — kein Scrollen
- Echtzeit-Warenkorb mit Summe, Mengen-Buttons und Leeren-Funktion
- Synthesized Web-Audio-Sounds: Kassen-Piep, Siegesfanfare, Fehlerbuzz
- Vollbild-Zahlungsoverlay mit Kundenphoto, Unterschrift und automatischem 8-Sekunden-Countdown
- Automatischer NFC-Produkt-Scanner-Banner (Hand-Scanner Modus)
- Installierbar als PWA — kein Browser-Chrome, echtes App-Feeling

### 📲 Terminal-Smartphone (Portrait)
- **Android Chrome**: liest NFC-Karten direkt per `window.NDEFReader` (Web NFC)
- **iOS Safari**: Touchscreen-Kartenwahl mit Tap auf Avatar-Button
- NFC-Berechtigung einmalig aktivieren — wird dauerhaft in `localStorage` gespeichert
- **4 Zahlungsmodi** (im Admin konfigurierbar):
  1. **Direkt** — sofortige Zahlung nach Karten-Tap
  2. **Spielgeld-Modus** — Terminal verlangt beliebige 4-stellige PIN
  3. **Sicherheits-Modus** — exakt hinterlegter PIN der Karte wird geprüft
  4. **Unterschrift** — Kind zeichnet Unterschrift auf dem Touchscreen-Canvas
- **Hand-Scanner-Modus**: Im Leerlauf NFC-Tags an Produkte halten → Artikel direkt in den Warenkorb auf dem Tablet
- Konfigurierbarer Standby-Timeout (15 s – Nie)
- Installierbar als PWA — Vollbild, kein Browser

### 🧾 Kassenbons & Drucken
- **Visueller Drag & Drop Bon-Builder** im Admin — Blöcke per Drag verschieben, aktivieren/deaktivieren
  - Block-Typen: Shop-Name, Text, Trennlinie (gestrichelt/voll/leer), Metadaten (Bon-Nr / Datum / Zeit), Kunde, Artikelliste, Unterschrift, QR-Code
  - Live-Vorschau (thermopapier-genau) direkt neben dem Builder
- **PDF-Bon**: Jeder Bon als PDF im Browser druckbar — ohne Drucker (`/receipt/<id>`)
- **Muster-Bon** zum Testen der Layout-Einstellungen (`/receipt/preview`)
- **USB-Thermodrucker** (Epson ESC/POS, `python-escpos`) — optional, via Docker device mapping
- Konfigurierbares Papierformat: 58 mm / 80 mm
- Druckmodus: Immer / Nachfragen / Nie — mit Rate-Limiting

### 🔐 Admin-Panel (`/admin`)
- Touchscreen-PIN-Pad zur Eltern-Authentifizierung (Standard: `1234`)
- **Dashboard**: KPI-Kacheln, 7-Tage-Umsatzchart, Top-Produkte, Top-Kunden, letzte Einkäufe
- **Produkte**: CRUD mit Bild-Upload, Emoji-Picker, Preis in Cent, Kategorie, NFC-UID (live scannen)
- **Kategorien**: CRUD mit Emoji-Picker, Sortierung, Aktiv/Inaktiv
- **Kundenkarten**: NFC-Registrierung per Tap, Foto, PIN, Aktiv/Inaktiv
- **Transaktionen**: vollständige Kaufhistorie mit Bon-Link, Einzellöschung, Komplett-Reset
- **Einstellungen**: Shop-Name, Admin-PIN, NFC-Modus, Hand-Scanner, Terminal-Timeout, Debug-Modus, Bon-Builder, Druckeroptionen
- **SSL/HTTPS**: Zertifikat & privaten Schlüssel direkt im Browser hochladen — kein SSH nötig
- Installierbar als PWA

### 🔌 REST API
| Endpunkt | Methode | Beschreibung |
|---|---|---|
| `/api/health` | GET | Service-Health-Check |
| `/api/products` | GET | Alle aktiven Produkte als JSON |
| `/api/products/by_nfc/<uid>` | GET | Produkt per NFC-UID suchen |
| `/api/cards` | GET | Alle aktiven Kunden-Karten |
| `/api/nfc_tap` | GET/POST | NFC-Tap per Webhook auslösen (iOS Shortcuts, Home Assistant, etc.) |
| `/api/print_receipt/<tx_id>` | POST | Thermaldruck eines Bons auslösen |

### 🧪 Dev-Simulator
Bei aktivem `DEV_MODE` erscheint ein 🧪-Button auf der Kasse. Ein Klick öffnet ein Drawer-Panel mit:
- **Schnell-Testkarten**: 1-Klick-Tap als Lena 👧, Papa 👨 oder unbekannte Karte ❓
- **Custom NFC-UID**: beliebige UID manuell eingeben und simulieren
- **PIN simulieren**: PIN `1234` direkt eintippen
- **Schnelllinks**: Terminal öffnen, letzten Bon als PDF ansehen, Admin-Panel öffnen

> Dev-Modus in den Admin-Einstellungen oder per `.env` (`DEV_MODE=false`) für den produktiven Betrieb deaktivieren.

---

## 🚀 Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket

# 2. Umgebungsdatei erstellen & anpassen
cp .env.example .env

# 3. Docker Container starten
docker compose up -d
```

Danach erreichbar unter:

| URL | Was |
|---|---|
| `http://localhost` | Kassen-Tablet |
| `http://localhost/terminal` | Terminal (Smartphone) |
| `http://localhost/admin` | Admin-Panel (PIN: `1234`) |
| `http://localhost/receipt/preview` | Muster-Bon (PDF) |

---

## 📚 Dokumentation

| Datei | Inhalt |
|---|---|
| [docs/setup.md](./docs/setup.md) | Raspberry Pi, Smartphone & Tablet einrichten |
| [docs/HTTPS_SETUP.md](./docs/HTTPS_SETUP.md) | SSL-Zertifikat für Web NFC (Android Chrome) |
| [CHANGELOG.md](./CHANGELOG.md) | Versionshistorie |

---

## 📄 Lizenz

MIT — Viel Spaß beim Spielen! 🛒✨
