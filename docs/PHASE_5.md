# Phase 5 Documentation — NFC Reader Service & Touchscreen Terminal (Pi #2)

## Summary of Completed Work
Phase 5 implements the second Raspberry Pi (#2) terminal system, combining real-time NFC tag polling, touchscreen display animations, PIN-Pad overlays, and a fallback **Touchscreen Card Selector Mode** when physical NFC hardware is not connected.

### Key Features Implemented:
1. **NFC Reader Python Service (`nfc_reader/reader.py`)**:
   - Polling loop for PN532 NFC reader module (I2C bus or USB Serial FT232/AZDelivery adapter).
   - Emits `card_tapped` WebSocket event to Pi #1 backend server upon tag detection.
   - Includes systemd auto-start service (`supermarkt-nfc.service`).

2. **Touchscreen Terminal Display UI (`/terminal`)**:
   - Full-screen animated cashier state machine:
     - **IDLE**: Welcome screen with shop logo.
     - **WAITING FOR PAYMENT**: Animated pulsing card reader graphic + order total.
     - **TOUCHSCREEN CARD SELECTOR**: If hardware NFC is disabled in settings (`nfc_mode="touchscreen_simulation"`), renders big touchable customer card buttons directly on screen!
     - **PIN PROMPT**: Touchscreen PIN-Pad overlay (`1-9`, `C`, `0`, `✓`) for PIN verification.
     - **SUCCESS**: Green checkmark + customer child photo animation + success sound.
     - **ERROR**: Friendly error display for unknown cards or wrong PINs.
     - **STANDBY**: Automatic screen standby / sleep mode after 30s inactivity (configurable).

3. **Configurable NFC Modes (`/admin/settings`)**:
   - **Hardware NFC-Lesegerät (`hardware`)**: Listens for physical NFC tag taps via PN532.
   - **Touchscreen-Kartenwahl (`touchscreen_simulation`)**: Allows children to tap their card photo/name directly on the touchscreen terminal screen without any NFC hardware!

---

## Phase 5 Checklist

- [x] PN532 NFC Reader service script (`nfc_reader/reader.py`)
- [x] WebSocket client connection to Pi #1 server
- [x] Touchscreen terminal view (`/terminal`)
- [x] Card tap animations, success checkmark, customer photo display
- [x] Touchscreen PIN-Pad prompt overlay
- [x] Touchscreen Card Selector Mode (`nfc_mode="touchscreen_simulation"`)
- [x] Configurable display standby / sleep timeout (30s default)
- [x] Systemd auto-start setup guide (`supermarkt-nfc.service`)
