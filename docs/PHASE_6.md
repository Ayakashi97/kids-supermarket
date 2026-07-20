# Phase 6 Documentation — Admin Panel (Product & Card Management, PIN-Pad, Settings)

## Summary of Completed Work
Phase 6 delivers a PIN-protected management interface for parents to administer products, register and edit customer cards, upload photos, view transaction histories, customize receipt layouts, and configure shop settings.

### Key Features Implemented:
1. **Touchscreen PIN-Pad Authentication (`/admin/login`)**:
   - Touch-friendly 3x4 numeric keypad (`1-9`, `C`, `0`, `✓`) designed for tablets and touch displays.
   - Visual masked PIN dots (`••••`) with onscreen feedback and keyboard support (0-9, Backspace, Enter).
   - Configurable PIN stored in DB settings (default: `1234`).

2. **Dashboard Overview (`/admin`)**:
   - Real-time statistics counters for total products, registered NFC customer cards, total transaction count, and accumulated play-money revenue.
   - Table of recent transactions.

3. **Product Management (`/admin/products`)**:
   - Full CRUD support: Add new products with name, price in Euros, category (*Obst & Gemüse, Backwaren, Milchprodukte, Getränke, Süßes, Sonstiges*), emoji symbol, and custom image file uploads (`static/images/cards/`).
   - Toggle product active/inactive state to temporarily hide items from the cashier tablet without deleting.

4. **NFC Customer Card Management & Editing (`/admin/cards` & `/admin/cards/edit/<id>`)**:
   - Real-time NFC enrollment: Click "Scan 💳" → server enters `waiting_for_registration` mode → tap card on Pi #2 NFC reader → captured UID automatically fills into form.
   - Attach child name (e.g. "Lena"), optional 4-digit PIN, + upload customer photo image (`static/images/cards/`).
   - **Card Editing (`/admin/cards/edit/<id>`)**: Edit child name, assign/change 4-digit PIN, update customer photo.
   - Display cards list with photo thumbnail, UID code, PIN, creation timestamp, active status, and action buttons.

5. **Configurable Settings & Bon-Layout (`/admin/settings`)**:
   - Shop name customization (e.g., *"Kinder-Markt"*).
   - Change admin PIN.
   - **Terminal PIN-Abfrage (`pin_mode`)**: Choose between **Deaktiviert** (instant checkout), **Spielgeld-Modus** (accepts any 4-digit PIN), or **Sicherheits-Modus** (verifies exact card PIN).
   - Thermal receipt printer controls: Enable/Disable printer, USB device path (`/dev/usb/lp0`), paper width (58mm / 80mm), header & footer text, show/hide customer card name, and show/hide date/time.
   - **"Bon Vorschau / PDF 📄"** button to preview layout changes in real time.

6. **Transaction History & PDF Export (`/admin/transactions`)**:
   - Comprehensive audit log of past sales including receipt number, timestamp, customer card holder name, itemized product list, total amount, status, and direct links to view/export each receipt as a printable PDF file (`/receipt/<tx_id>`).

---

## Phase 6 Checklist

- [x] Admin login `/admin` with touchscreen PIN-Pad authentication
- [x] Dashboard stats (products count, cards count, total transactions, play money total)
- [x] Product CRUD (name, price in cents, category, emoji/image upload)
- [x] Card Management (`/admin/cards`): register new card by NFC tap, edit card (`/admin/cards/edit/<id>`), set 4-digit PIN, name, photo upload, toggle active, delete
- [x] Settings UI (`/admin/settings`): Shop name, admin PIN, Terminal PIN mode (`pin_mode`), printer enable toggle, device path, paper width, header/footer customization, show/hide card name
- [x] Receipt PDF / Printable exporter (`/receipt/<tx_id>` & `/receipt/preview`)
- [x] Transaction history viewer (`/admin/transactions`)
