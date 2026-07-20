# 🛒 Kinder-Supermarkt (Kids Supermarket Play System)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/Flask-SocketIO-000000.svg)](https://flask.palletsprojects.org/)

Ein interaktives, kinderfreundliches Spiel-Supermarktsystem für Kinder ab 3 Jahren. 
Bestehend aus einer **Kassen-App auf dem Tablet**, einem **Raspberry Pi Server**, einem **Raspberry Pi 2 Touchscreen-Terminal mit PN532 NFC-Kartenleser**, einem **USB-Thermodrucker** sowie **PDF-Kassenbon-Export**.

---

## 🌟 Highlights & Funktionen

- **📱 Kinderleichte Kassen-Oberfläche (Tablet-UI)**:
  - Große bunten Tasten, Kategorien-Filter (*Obst & Gemüse 🍎, Backwaren 🥨, Milchprodukte 🥛, Getränke 🧃, Süßes 🍫*), klare Preisanzeige und kinderfreundliche Animationen.
  - Sound-Effekte über Web Audio API (Kassen-Piep beim Tippen, Sieges-Fanfaren bei Bezahlung, Fehler-Buzz).
  - Minimaler Text, intuitive Bedienung für kleine Kinder.

- **💳 NFC-Zahlungsterminal mit Touchscreen (Raspberry Pi #2)**:
  - Läuft im Kiosk-Modus mit visuellen Live-Animationen (*Pulsierendes Lesegerät, Grünes Häkchen, Kundenfoto des Kindes*).
  - Eigenständiger Python-Dienst liest PN532 NFC-Karten/Chips aus und kommuniziert in Echtzeit über WebSockets mit dem Server.

- **🧾 Echter Thermobon-Druck & PDF-Bon-Export**:
  - Druckt automatische Kassenbons über USB-Thermodrucker (`python-escpos`).
  - **PDF-Kassenbon Generator**: Jeder Bon kann direkt im Browser angesehen, als PDF gespeichert oder auf normalen Druckern ausgedruckt werden.
  - Sämtliche Bon-Zeilen (Supermarkt-Name, Header, Footer, Papierbreite 58mm/80mm, Kundenname an/aus, Datum/Uhrzeit) sind im Admin-Panel anpassbar.

- **🔐 Touchscreen PIN-Pad Admin-Panel (`/admin`)**:
  - Großes 3x4 Touchscreen PIN-Pad zur Eltern-Authentifizierung (Standard-PIN: `1234`).
  - Produkt-Verwaltung (CRUD mit Bild-Upload & Preisen in Euro/Cent).
  - NFC-Kundenkarten Registrierung: Karte an den Pi #2 halten, Name & Foto des Kindes zuweisen.
  - Transaktions-Historie aller getätigten Einkäufe.

- **🧪 Entwicklungs- & Simulations-Modus (`DEV_MODE=true`)**:
  - Testen des gesamten Systems auf einem normalen Laptop ohne physischen Raspberry Pi oder NFC-Leser.
  - Einblenden einer **DEV SIMULATOR** Toolbar zum 1-Klick Auslösen von Test-Karten (*👧 Lena, 👨 Papa, ❓ Unbekannt*) sowie Schnelllinks zum Terminal und PDF-Bon.

---

## 📐 Hardware-Architektur

```
[Tablet / Browser]  <──HTTP/WebSocket──>  [Raspberry Pi #1: Backend Server]
 (Kassen-Display)                                   │
                                          ┌─────────┴──────────┐
                                          │                    │
                               [USB Thermal Printer]  [Raspberry Pi #2: NFC Reader]
                                                              │
                                                      [PN532 NFC Module + Touchscreen Display]
```

| Gerät | Rolle | Betriebssystem | Angeschlossene Hardware | Standard-URL |
|---|---|---|---|---|
| **Raspberry Pi #1** | Server (Flask, DB, Docker) | Raspberry Pi OS Lite (64-bit) | USB Thermodrucker (Epson etc.) | `http://<pi1-ip>:5050` |
| **Raspberry Pi #2** | NFC-Leser & Terminal-Display | Raspberry Pi OS Desktop (64-bit) | Touchscreen Display + PN532 NFC Modul | `http://<pi1-ip>:5050/terminal` |
| **Tablet** | Kassen-Display | iOS / Android / Webbrowser | Keine | `http://<pi1-ip>:5050` |

---

## 🚀 Schnellstart (Docker Compose)

Das gesamte Backend wird vorkonfiguriert über Docker Compose gestartet:

```bash
# 1. Repository klonen
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket

# 2. Umgebungsdatei erstellen
cp .env.example .env

# 3. Docker Container starten
docker compose up -d
```

Nach dem Start ist das System direkt erreichbar unter:
- **Kasse (Tablet UI)**: `http://localhost:5050`
- **Touchscreen Terminal**: `http://localhost:5050/terminal`
- **Admin Panel**: `http://localhost:5050/admin` (PIN: `1234`)
- **Muster-Bon (PDF)**: `http://localhost:5050/receipt/preview`

---

## 🛠️ Ausführliche Dokumentation

Sämtliche Guides und System-Spezifikationen befinden sich im Order [`docs/`](./docs):

- 📘 **[GEMINI.md](./GEMINI.md)** — Repository-Regeln, Tech-Stack & Gesamtübersicht
- 🛠️ **[Raspberry Pi Hardware & OS Setup Guide](./docs/setup.md)** — Vollständige Anleitung zum Flashen von Pi #1 & Pi #2, PN532 Verkabelung (I2C/SPI), Chromium Kiosk-Modus & Auto-Start Dienste
- 🧪 **[Development & Emulation Mode Guide](./docs/DEV_MODE.md)** — Testen ohne Hardware über die Entwickler-Simulationsleiste
- 📋 **[Master Phase Progress Checklist](./docs/CHECKLIST.md)** — Übersicht über alle 7 Entwicklungsphasen
- 📄 **Phase-Dokumentationen**:
  - [Phase 1: Foundation & Docker Setup](./docs/PHASE_1.md)
  - [Phase 2: Cashier UI & Audio Synthesizer](./docs/PHASE_2.md)
  - [Phase 3: Payment Flow & Socket State Machine](./docs/PHASE_3.md)
  - [Phase 4: Receipt Printing & PDF Generator](./docs/PHASE_4.md)
  - [Phase 5: Touchscreen Terminal & PN532 Reader](./docs/PHASE_5.md)
  - [Phase 6: Admin Panel & PIN-Pad Login](./docs/PHASE_6.md)

---

## 💻 Tech Stack

- **Backend**: Python 3.11+, Flask, Flask-SocketIO, Flask-SQLAlchemy
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript (keine schweren Frameworks)
- **Kommunikation**: WebSockets (Flask-SocketIO) für Echtzeit-Synchronisation
- **Datenbank**: SQLite (gespeichert im Docker-Volume)
- **Drucker**: USB Thermodrucker (`python-escpos`) + HTML/CSS Print Exporter
- **Containerisierung**: Docker + Docker Compose

---

## 📄 Lizenz
Dieses Projekt steht unter der [MIT Lizenz](LICENSE). Viel Spaß beim Spielen! 🛒✨
