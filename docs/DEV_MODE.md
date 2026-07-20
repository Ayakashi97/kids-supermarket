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

2. **Browser-Based NFC Emulation & PDF Toolbar**:
   - Displays a floating **DEV SIMULATOR** bar at the bottom right of the browser pages.
   - Includes 1-click test buttons:
     - `👧 Lena` (Simulates tapping Lena's NFC card)
     - `👨 Papa` (Simulates tapping Papa's NFC card)
     - `❓ Unbekannt` (Simulates tapping an unregistered NFC card)
     - Custom UID input box + `Tap 💳` button.
   - **`📄 Bon (PDF)`**: 1-click button to open, view, and print/download the generated PDF receipt of the latest transaction.
   - **`📺 Terminal`**: Opens the Pi #2 Touchscreen Terminal UI in a separate browser tab for side-by-side real-time synchronization testing.

3. **PDF Receipt Generator & Web Preview**:
   - Route `/receipt/<tx_id>` and `/receipt/latest` render a printable thermal receipt matching the configured paper width (58mm or 80mm).
   - Click "Drucken / als PDF speichern 📄" to open the browser print dialog and save receipts as PDF files directly on your computer!

4. **NFC Console Simulator (`nfc_reader/reader.py --simulate`)**:
   - Running `python reader.py --simulate` provides an interactive terminal prompt where you can type any UID (e.g., `TEST_LENA_123`) to simulate physical card taps over WebSockets.

5. **Mock Thermal Printer Output**:
   - If a physical USB thermal printer is not connected to `/dev/usb/lp0`, the receipt printing service formats the receipt and logs the output directly to stdout without failing or interrupting the checkout flow.

---

## 🧪 Step-by-Step Testing Workflow

1. Start application with Docker Compose:
   ```bash
   docker-compose up -d
   ```
2. Open Cashier UI in browser: `http://localhost:5050`
3. Open Terminal UI in a second browser tab or window: `http://localhost:5050/terminal`
4. On the Cashier UI:
   - Tap items (*e.g., Brezel 🥨, Apfel 🍎*) to add them to the shopping cart.
   - Tap **"Bezahlen 💳"**.
   - Observe both Cashier and Terminal screens transition to *"Karte jetzt anhalten! 💳"*.
5. On the Dev Simulator bar (bottom right):
   - Click **`👧 Lena`**.
6. Observe:
   - Cashier UI plays victory fanfare 🎉 and displays *"Hallo Lena! 🎉"*.
   - Terminal UI displays Lena's greeting & confirmation animation.
   - Click **`📄 Bon (PDF)`** on the toolbar to preview, print, or save the receipt as a PDF file!
