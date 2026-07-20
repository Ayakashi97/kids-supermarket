# Phase 6 Documentation — Admin Panel (Product & Card Management)

## Summary of Completed Work
Phase 6 delivers a PIN-protected management interface for parents to administer products, register customer cards, upload photos, view transaction histories, and configure shop settings.

### Key Features Implemented:
1. **PIN-Protected Authentication (`/admin/login`)**:
   - Protected routes checking admin session status.
   - Configurable PIN stored in DB settings (default: `1234`).

2. **Dashboard Overview (`/admin`)**:
   - Real-time statistics counters for total products, registered NFC customer cards, total transaction count, and accumulated play-money revenue.
   - Table of recent transactions.

3. **Product Management (`/admin/products`)**:
   - Full CRUD support: Add new products with name, price in Euros, category (*Obst & Gemüse, Backwaren, Milchprodukte, Getränke, Süßes, Sonstiges*), emoji symbol, and custom image file uploads (`static/images/products/`).
   - Toggle product active/inactive state to temporarily hide items from the cashier tablet without deleting.
   - Soft or permanent deletion.

4. **NFC Customer Card Management & Photo Registration (`/admin/cards`)**:
   - Real-time NFC enrollment: Click "Scan 💳" → server enters `waiting_for_registration` mode → tap card on Pi #2 NFC reader → captured UID automatically fills into form.
   - Attach child name (e.g. "Lena") + upload customer photo image (`static/images/cards/`).
   - Display cards list with photo thumbnail, UID code, creation timestamp, active status, and action buttons (toggle active/inactive, delete).

5. **Configurable Settings (`/admin/settings`)**:
   - Shop name customization (e.g., "Kinder-Markt").
   - Admin security PIN change.
   - Thermal receipt printer configuration:
     - Enable / disable receipt printer toggle (`printer_enabled`).
     - System device path (`printer_device`, e.g. `/dev/usb/lp0`).
     - Customizable receipt header & footer text.

6. **Transaction History (`/admin/transactions`)**:
   - Comprehensive audit log of past sales including receipt number, timestamp, customer card holder name, itemized product list, total amount, and status.

---

## Phase 6 Checklist

- [x] Admin login `/admin` with PIN authentication
- [x] Dashboard stats (products count, cards count, total transactions, play money total)
- [x] Product CRUD (name, price in cents, category, emoji/image upload)
- [x] Card Management (`/admin/cards`): register new card by NFC tap, name, photo upload, toggle active, delete
- [x] Settings UI (`/admin/settings`): Shop name, admin PIN, printer enable toggle, device path, header & footer customization
- [x] Transaction history viewer (`/admin/transactions`)
