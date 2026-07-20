# 🛒 Kinder-Supermarkt (Kids Supermarket Play System)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/Flask-SocketIO-000000.svg)](https://flask.palletsprojects.org/)

Ein interaktives, kinderfreundliches Spiel-Supermarktsystem für Kinder ab 3 Jahren. 
Bestehend aus einer **Kassen-App auf dem Tablet**, einem **Raspberry Pi Server**, einem **Smartphone als NFC-Zahlungsterminal (Web NFC & PWA)**, einem **USB-Thermodrucker** sowie **PDF-Kassenbon-Export**.

---

## 🌟 Highlights & Funktionen

- **📱 Kinderleichte Kassen-Oberfläche (Tablet-PWA)**:
  - Große bunten Tasten, Kategorien-Filter (*Obst & Gemüse 🍎, Backwaren 🥨, Milchprodukte 🥛, Getränke 🧃, Süßes 🍫*), klare Preisanzeige und kinderfreundliche Animationen.
  - Dynamischer Supermarkt-Name: Im Admin-Panel einstellbar (z.B. *Emmis Kaufladen*, *Kinder-Supermarkt* oder *Lenas Mini-Markt*) und sofort live auf Kasse, Terminal & Bons aktiv!
  - Sound-Effekte über Web Audio API (Kassen-Piep beim Tippen, Sieges-Fanfaren bei Bezahlung, Fehler-Buzz).
  - Ergonomischer Einkaufskorb ohne Abschneiden von Knöpfen, mit Touch-Schaltflächen für Kinderhände.

- **📲 Altes Smartphone als NFC-Zahlungsterminal (Web NFC & PWA Fullscreen)**:
  - Benutze einfach ein **altes Smartphone (Android mit NFC oder iPhone)** statt eines zweiten Raspberry Pis!
  - **Android Chrome**: Liest NFC-Karten/Sticker direkt über den eingebauten NFC-Chip im Smartphone aus (`window.NDEFReader`).
  - **Dauerhafte Berechtigung**: Nach der ersten NFC-Aktivierung merkt sich die App die Erlaubnis im `localStorage` – der grüne Aktivierungsbutton verschwindet danach dauerhaft.
  - **iOS Safari / PWA**: Funktioniert als installierbare App ("Zum Home-Bildschirm hinzufügen") im 100% Vollbildmodus mit visuellen Live-Animationen, Touchscreen-Kartenwahl und PIN-Eingabe.
  - **3 Konfigurierbare PIN-Modi** (im Admin-Panel einstellbar):
    1. **Deaktiviert**: Sofortige Bezahlung nach Auflegen der Karte.
    2. **Spielgeld-Modus (`any_4_digits`)**: Terminal verlangt 4-stellige PIN, akzeptiert jede Zahlenkombination für echtes EC-Karten-Spielgefühl.
    3. **Sicherheits-Modus (`exact_match`)**: Terminal prüft exakte 4-stellige PIN der Kundenkarte (Standard: `1234`).

- **🧾 Echter Thermobon-Druck & PDF-Bon-Export**:
  - Druckt automatische Kassenbons über USB-Thermodrucker (`python-escpos`).
  - **PDF-Kassenbon Generator**: Jeder Bon kann direkt im Browser angesehen, als PDF gespeichert oder auf normalen Druckern ausgedruckt werden.
  - Sämtliche Bon-Zeilen (Supermarkt-Name, Header, Footer, Papierbreite 58mm/80mm, Kundenname an/aus, Datum/Uhrzeit) sind im Admin-Panel anpassbar.

- **🔐 Touchscreen PIN-Pad Admin-Panel (`/admin`)**:
  - Großes 3x4 Touchscreen PIN-Pad zur Eltern-Authentifizierung (Standard-PIN: `1234`).
  - Produkt-Verwaltung (CRUD mit Bild-Upload & Preisen in Euro/Cent).
  - NFC-Kundenkarten Registrierung: Karte an das Smartphone / Lesegerät halten (Hardware UID oder NDEF Text), Name, optionale PIN & Foto des Kindes zuweisen.
  - Transaktions-Historie aller getätigten Einkäufe.

- **🧪 Entwicklungs- & Simulations-Modus (`DEV_MODE=true`)**:
  - Testen des gesamten Systems auf einem normalen Laptop ohne physische Hardware.
  - Einblenden einer **DEV SIMULATOR** Toolbar zum 1-Klick Auslösen von Test-Karten (*👧 Lena, 👨 Papa, ❓ Unbekannt*), PIN-Simulation (*PIN 1234 🔢*) sowie Schnelllinks zum Terminal und PDF-Bon.

---

## 📐 Hardware-Architektur

```
[Tablet / Browser (Kasse)] <──HTTP/WebSocket──> [Raspberry Pi #1: Backend Server] <──HTTP/WebSocket──> [Smartphone (Terminal PWA + Web NFC)]
                                                            │
                                                  [USB Thermal Printer]
```

| Gerät | Rolle | Betriebssystem | PWA Name | Standard-URL |
|---|---|---|---|---|
| **Raspberry Pi #1** | Server (Flask, DB, Docker) | Raspberry Pi OS Lite (64-bit) | — | `http://<pi1-ip>:5050` |
| **Tablet** | Kassen-Display | iOS / Android / Webbrowser | **Supermarkt Kasse** 🛒 | `http://<pi1-ip>:5050` |
| **Smartphone** | Terminal & NFC-Reader | Android (Chrome Web NFC) / iOS (PWA Vollbild) | **Supermarkt Terminal** 💳 | `http://<pi1-ip>:5050/terminal` |

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
- **Zahlungsterminal (Smartphone PWA)**: `http://localhost:5050/terminal`
- **Admin Panel**: `http://localhost:5050/admin` (PIN: `1234`)
- **Muster-Bon (PDF)**: `http://localhost:5050/receipt/preview`

---

## 🛠️ Ausführliche Dokumentation

Sämtliche Guides und System-Spezifikationen befinden sich im Ordner [`docs/`](./docs):

- 📘 **[GEMINI.md](./GEMINI.md)** — Repository-Regeln, Tech-Stack & Gesamtübersicht
- 🛠️ **[Raspberry Pi & Smartphone Setup Guide](./docs/setup.md)** — Anleitung für Smartphone Web NFC & PWA Installation auf iPhone / Android
- 🧪 **[Development & Emulation Mode Guide](./docs/DEV_MODE.md)** — Testen ohne Hardware über die Entwickler-Simulationsleiste
- 📋 **[Master Phase Progress Checklist](./docs/CHECKLIST.md)** — Übersicht über Entwicklungsphasen
- 📱 **[Phase 8 PWA & Web NFC Documentation](./docs/PHASE_8.md)** — Details zur Smartphone PWA & Web NFC Integration

---

## 📄 Lizenz
Dieses Projekt steht unter der [MIT Lizenz](LICENSE). Viel Spaß beim Spielen! 🛒✨
