# 🧪 Development & Testing Emulation Mode (`DEV_MODE`)

## Overview
The **Kinder-Supermarkt** system includes a built-in development and testing mode enabled via the `DEV_MODE=true` environment variable. This allows developers and parents to test the entire multi-device workflow (Tablet ↔ Backend ↔ Touchscreen Terminal ↔ Thermal Printer) without requiring physical hardware (such as Raspberry Pi #2 or physical PN532 NFC readers).

---

## 🚀 How to Enable Development Mode

In your `.env` file (or Docker Compose environment):

```env
DEV_MODE=true
```

When enabled:
1. **Automatic Test Data Seeding**:
   - Seeds 12 default German products (*Brezel, Apfel, Banane, etc.*).
   - Seeds 2 test customer cards:
     - **Lena 👧** (UID: `TEST_LENA_123`)
     - **Papa 👨** (UID: `TEST_PAPA_456`)

2. **Browser-Based NFC & PIN Emulation Toolbar**:
   - Displays a floating **DEV SIMULATOR** bar at the bottom right of the browser pages.
   - Includes 1-click test buttons:
     - `👧 Lena` (Simulates tapping Lena's NFC card)
     - `👨 Papa` (Simulates tapping Papa's NFC card)
     - `❓ Unbekannt` (Simulates tapping an unregistered NFC card)
     - Custom UID input box + `Tap 💳` button.
     - `PIN 1234 🔢` (Simulates submitting PIN '1234' over WebSockets).
   - **`📄 Bon (PDF)`**: 1-click button to open, view, and print/download the generated PDF receipt of the latest transaction.
   - **`📺 Terminal`**: Opens the Pi #2 Touchscreen Terminal UI in a separate browser tab for side-by-side real-time synchronization testing.

3. **Configurable Terminal PIN Modes (`pin_mode`)**:
   - Admin panel (`/admin/settings`) supports 3 Terminal PIN modes:
     - **Deaktiviert (`disabled`)**: Payment completes immediately after card tap.
     - **Spielgeld-Modus (`any_4_digits`)**: Terminal prompts for a 4-digit PIN, accepts ANY 4 numbers for a fun play-money checkout experience.
     - **Sicherheits-Modus (`exact_match`)**: Terminal prompts for PIN and verifies it matches the card holder's assigned 4-digit PIN (or default `1234`).

4. **PDF Receipt Generator & Web Preview**:
   - Route `/receipt/<tx_id>` and `/receipt/latest` render a printable thermal receipt matching the configured paper width (58mm or 80mm).
   - Click "Drucken / als PDF speichern 📄" to open the browser print dialog and save receipts as PDF files directly on your computer!

5. **Mock Thermal Printer Output**:
   - If a physical USB thermal printer is not connected to `/dev/usb/lp0`, the receipt printing service formats the receipt and logs the output directly to stdout without failing or interrupting the checkout flow.
