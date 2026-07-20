# Phase 5 Documentation — NFC Reader Service & Touchscreen Terminal (Pi #2)

## Summary of Completed Work
Phase 5 implements the hardware reader service and touchscreen terminal display for Raspberry Pi #2.

### Key Components Implemented:
1. **Touchscreen Terminal View (`app/templates/terminal.html` & `/terminal` route)**:
   - Dedicated full-screen terminal interface designed for Pi #2 touchscreen in Kiosk Mode.
   - Real-time animated screens:
     - **Idle Screen**: Displays welcome title (*"Kinder-Supermarkt — Bereit für die nächste Bestellung"*).
     - **Waiting Screen**: Displays large pulsing card reader icon (`💳`) and live total amount.
     - **Success Screen**: Displays celebratory card holder photo, greeting (*"Hallo Lena! 🎉"*), and confirmation.
     - **Error Screen**: Displays friendly error icon and message (*"Unbekannte Karte 😕"*).

2. **Standalone NFC Reader Script (`nfc_reader/reader.py`)**:
   - Communicates with hardware PN532 via CircuitPython I2C driver (`adafruit-circuitpython-pn532`).
   - Connects to Pi #1 Flask-SocketIO backend server.
   - Debounce logic: 3-second rate limiter on repeated taps for the same UID.
   - Automatic hardware fallback to console simulation mode (`--simulate`).

3. **Pi #2 Systemd Auto-Start**:
   - `supermarkt-nfc.service`: Service definition for auto-starting the NFC reader service on Pi #2 boot.
   - Setup instructions in `nfc_reader/README.md`.

---

## Phase 5 Checklist

- [x] Dedicated terminal route `/terminal` for Pi #2 touchscreen (browser kiosk mode)
- [x] Real-time payment animations on Pi #2 display (waiting pulse, card tapping animation, success photo overlay)
- [x] Standalone Python script `nfc_reader/reader.py`
- [x] PN532 module connection (SPI/I2C via `nfcpy`/`pn532`)
- [x] Connect to Pi #1 Flask-SocketIO server and emit `card_tapped`
- [x] Rate-limit repeated taps (3s debounce)
- [x] Systemd service script for Pi #2 auto-start
