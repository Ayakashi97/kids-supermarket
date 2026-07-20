# 🧪 Development, Emulation & Touchscreen Simulator Guide

This guide explains how to test and run the full **Kinder-Supermarkt** application without physical Raspberry Pi hardware, thermal printers, or NFC reader boards.

---

## 🚀 Overview of Emulation Features

The system includes built-in emulation modes so you can develop and play on any computer or tablet:

1. **🧪 DEV SIMULATOR Bar** (Visible on top of the Cashier UI):
   - Simulated NFC Card Taps (`Tap 👧 Lena`, `Tap 👨 Papa`, `Tap ❓ Unbekannt`).
   - Terminal PIN Entry Simulation (`PIN 1234 🔢`).
   - Immediate Bon PDF Receipt view (`📄 Bon (PDF)`).
2. **📱 Touchscreen Card Selector Mode (`nfc_mode="touchscreen_simulation"`)**:
   - In Admin Panel under **`/admin/settings`**, switch **NFC-Lesegerät Modus** to **"Touchscreen-Kartenwahl auf Terminal (Keine Hardware erforderlich)"**.
   - When a transaction is started on the tablet cashier view, the terminal screen at `/terminal` presents large touchable customer card buttons directly on screen!
   - Children or testers tap their photo/name directly on the touchscreen terminal to simulate tapping a physical NFC card.
3. **📄 Virtual PDF Receipt Engine (`/receipt/<tx_id>`)**:
   - Generates exact 58mm / 80mm printable thermal receipts in your browser with print/PDF support.

---

## 🛠️ Step-by-Step Testing Guide

### 1. Enable Touchscreen Card Selector Mode in Admin Settings
1. Navigate to `http://localhost:5050/admin/settings`.
2. Login with PIN `1234`.
3. Under **NFC-Lesegerät Modus**, select **"Touchscreen-Kartenwahl auf Terminal (Keine Hardware erforderlich)"**.
4. Save settings.

### 2. Test Checkout Flow on Terminal Display
1. Open Cashier UI: `http://localhost:5050`
2. Open Terminal Display: `http://localhost:5050/terminal`
3. Add products to cart on Cashier UI and click **"Jetzt Bezahlen (💳 Karte)"**.
4. Watch the Terminal Display at `/terminal`:
   - It shows a friendly card selection grid with buttons for each active child/customer card!
   - Tap **"Lena"** on the touchscreen terminal.
   - If PIN protection is enabled, enter PIN `1234` on the terminal's touchscreen PIN-Pad.
   - Payment completes instantly with success fanfare and customer photo animation!
