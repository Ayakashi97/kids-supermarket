# Phase 5 Documentation — Touchscreen Terminal & PN532 NFC Reader (Pi #2)

## Summary of Completed Work
Phase 5 implements the standalone touchscreen terminal interface served at `/terminal` and the standalone Python service running on Raspberry Pi #2.

### Key Features Implemented:
1. **Touchscreen Terminal View (`/terminal`)**:
   - Designed specifically for Raspberry Pi #2 connected to a touchscreen display in Chromium Kiosk Mode.
   - States & Animations:
     - **IDLE**: Welcome screen (*"Kinder-Supermarkt — Bereit für die nächste Bestellung"*).
     - **WAITING FOR PAYMENT**: Pulsing card reader graphic with gold drop-shadow glow and total amount display (*"Karte jetzt anhalten! 💳"*).
     - **PROMPT PIN**: Interactive 3x4 Touchscreen PIN-Pad (`1-9`, `C`, `0`, `✓`) with masked PIN dots (`••••`).
     - **PAYMENT SUCCESS**: Celebratory greeting with green photo frame display of child's customer picture or party emoji 🎉.
     - **PAYMENT ERROR**: Friendly error display (*"Unbekannte Karte 😕"* / *"Falsche PIN ❌"*).

2. **Configurable Terminal PIN Request Modes (`pin_mode`)**:
   - Three modes configurable via Admin Settings (`/admin/settings`):
     - `disabled`: Immediate payment processing upon card tap (no PIN prompt).
     - `any_4_digits`: Displays PIN-Pad on touchscreen, accepts any 4-digit input (play money experience for kids).
     - `exact_match`: Displays PIN-Pad on touchscreen, verifies PIN against the card's assigned 4-digit PIN (or default `1234`).

3. **Standalone NFC Reader Service (`nfc_reader/reader.py`)**:
   - Connects to PN532 NFC module via I2C (`/dev/i2c-1`) or SPI.
   - 3-second debounce rate-limiting to prevent duplicate card reads.
   - Emits `card_tapped` WebSocket event to Pi #1 Flask server.
   - Includes systemd service template `nfc_reader/supermarkt-nfc.service` for automatic start on boot.

---

## Phase 5 Checklist

- [x] Dedicated terminal route `/terminal` for Pi #2 touchscreen (browser kiosk mode)
- [x] Real-time payment animations on Pi #2 display (waiting pulse, touchscreen PIN-Pad, success photo overlay)
- [x] Configurable Terminal PIN-Pad modes (`disabled`, `any_4_digits`, `exact_match`)
- [x] Standalone Python script `nfc_reader/reader.py`
- [x] PN532 module connection (SPI/I2C via `adafruit-circuitpython-pn532` / `nfcpy`)
- [x] Connect to Pi #1 Flask-SocketIO server and emit `card_tapped`
- [x] Rate-limit repeated taps (3s debounce)
- [x] Systemd service script for Pi #2 auto-start
